from pathlib import Path
from typing import Set, Dict


class ModPath:
    def __init__(self) -> None:
        ...


class ModNode:
    """
    Represents a single Python file
    """

    def __init__(self, name: str, path: Path) -> None:
        self._name = name
        self._path = path

        self._imports: Set["ModNode"] = set()
        self._imported_by: Set["ModNode"] = set()

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def imports(self) -> Set["ModNode"]:
        """
        Get modules that are directly imported by the current one
        """
        return self._imports

    @property
    def imported_by(self) -> Set["ModNode"]:
        """
        Get modules that imports the current one
        """
        return self._imports


class ModGraph:
    """
    """

    def __init__(self) -> None:
        self._mods_by_path: Dict[Path, ModNode] = {}
        self._mods_by_name: Dict[str, ModNode] = {}
