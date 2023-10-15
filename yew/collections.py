import dataclasses
import logging
from importlib import util as importlib_util
from pathlib import Path
from typing import Dict, Final, List, Set, Tuple

logger = logging.getLogger(__name__)


class ModuleNotFound(Exception):
    """
    Raised when module spec is not found (this could be the case in optional imports)
    """


@dataclasses.dataclass(frozen=True)
class DirectImport:
    mod_name: "ModName"
    path: Path
    lineno: int
    col_offset: int


class ModName:
    SEP: Final[str] = "."

    def __init__(self, mod_parts: List[str]) -> None:
        self._mod_parts = mod_parts

    @property
    def parts(self) -> List[str]:
        return self._mod_parts

    @property
    def file_path(self) -> Path:
        mod_name = str(self)

        try:
            mod_spec = importlib_util.find_spec(mod_name)  # type: ignore[attr-defined]
        except (ModuleNotFoundError, ValueError):
            raise ModuleNotFound(f"Could not find package '{mod_name}' under Python path.") from None
        except Exception as e:
            raise ModuleNotFound(f"Could not import the module: {mod_name}") from e

        if not mod_spec:
            raise ModuleNotFound(f"Could not find package '{mod_name}' under Python path.")

        if mod_spec.origin:
            return Path(mod_spec.origin)

        return Path(mod_spec.loader_state.filename)

    @property
    def is_package(self) -> bool:
        file_path = self.file_path

        return file_path.stem == "__init__"

    def resolve(self, level_up: int) -> "ModName":
        if not level_up:
            return self

        return ModName(self._mod_parts[:-level_up])

    def __truediv__(self, part) -> "ModName":
        if isinstance(part, ModName):
            return ModName([*self._mod_parts, part.parts])

        if isinstance(part, str):
            return ModName([*self._mod_parts, part])

        raise NotImplementedError

    @classmethod
    def from_str(cls, mod_path: str) -> "ModName":
        return cls(mod_path.split(cls.SEP))

    @classmethod
    def from_path(cls, file_path: Path) -> "ModName":
        mod_path = list(file_path.with_suffix("").parts)

        if mod_path[-1] == "__init__":
            mod_path.pop()

        return cls(mod_path)

    @classmethod
    def from_object_path(cls, object_path: List[str]) -> Tuple["ModName", str | None]:
        original_obj_path = [*object_path]

        try:
            if not importlib_util.find_spec(cls.join(object_path)):
                raise ModuleNotFoundError

            return cls(object_path), None
        except ModuleNotFoundError:
            # we have found an object import (e.g. constant, class, function, etc)
            pass
        except Exception as e:
            raise ModuleNotFound(f"Could not import the module: {original_obj_path}") from e

        object_name = object_path.pop()

        try:
            importlib_util.find_spec(cls.join(object_path))

            return cls(object_path), object_name
        except ModuleNotFoundError:
            raise ModuleNotFound(f"{cls.join(original_obj_path)} could not be found") from None
        except Exception as e:
            raise ModuleNotFound(f"Could not import the module: {original_obj_path}") from e

    @classmethod
    def join(cls, parts: List[str]) -> str:
        try:
            return cls.SEP.join(parts)
        except TypeError:
            logger.warning(f"Type error on joining module parts: {parts}")
            raise

    @classmethod
    def split(cls, mod_name: str) -> List[str]:
        return mod_name.split(cls.SEP)

    def __str__(self) -> str:
        return self.join(self._mod_parts)

    def __repr__(self) -> str:
        return f'"{str(self)}"'


@dataclasses.dataclass(frozen=True)
class ImportContext:
    """
    A module import with code reference
    """

    lineno: int
    col_offset: int
    module: "Module"


class Module:
    """
    Represents a single Python module file
    """

    def __init__(self, mod_name: ModName, file_path: Path) -> None:
        self._mod_name = mod_name
        self._file_path = file_path

        self._imports: Set["ImportContext"] | None = None
        self._imported_by: Set["ImportContext"] = set()

    @property
    def mod_name(self) -> ModName:
        return self._mod_name

    @property
    def file_path(self) -> Path:
        return self._file_path

    @property
    def imports(self) -> Set["ImportContext"] | None:
        """
        Get modules that are directly imported by the current one
        """
        return self._imports

    @property
    def imported_by(self) -> Set["ImportContext"]:
        """
        Get modules that imports the current one
        """
        return self._imported_by

    def add_imports(self, imports: Set[ImportContext]) -> None:
        if self._imports is None:
            self._imports = set()

        self._imports.update(imports)


class ModGraph:
    """
    Module import graph
    """

    def __init__(self) -> None:
        self._mods_by_file_path: Dict[Path, Module] = {}
        self._mods_by_mod_name: Dict[ModName, Module] = {}

        self._unmet_nodes: Dict[ModName, Module] = {}

    def __getitem__(self, name: str | Path | ModName) -> Module | None:
        ...

    def add(self, mod_name: ModName, file_path: Path, direct_imports: Set[DirectImport]) -> None:
        """
        Add a new module to the graph
        """
        module = Module(mod_name, file_path)

        if self._unmet_nodes.get(mod_name):
            module = self._unmet_nodes.pop(mod_name)

        mod_imports: Set[ImportContext] = set()

        for direct_import in direct_imports:
            imported_module = self._mods_by_mod_name.get(direct_import.mod_name)

            if not imported_module:
                imported_module = Module(direct_import.mod_name, direct_import.path)
                self._unmet_nodes[direct_import.mod_name] = imported_module

            imported_module.imported_by.add(
                ImportContext(module=module, lineno=direct_import.lineno, col_offset=direct_import.col_offset)
            )

            mod_imports.add(
                ImportContext(module=imported_module, lineno=direct_import.lineno, col_offset=direct_import.col_offset)
            )

        module.add_imports(mod_imports)

        self._mods_by_file_path[module.file_path] = module
        self._mods_by_mod_name[module.mod_name] = module

    def __repr__(self) -> str:
        return f"ModGraph(modules={len(self._mods_by_file_path)})"
