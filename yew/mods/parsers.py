import ast
import logging
from typing import Any, Dict, List, Protocol, Set

from yew.collections import DirectImport, ModName, ModuleNotFound

logger = logging.getLogger(__name__)


class Parser(Protocol):
    def __call__(self, module_name: ModName, node: ast.AST) -> Set[DirectImport]:
        ...


class ImportParser:
    def __init__(self) -> None:
        ...

    def __call__(self, mod_name: ModName, node: ast.AST) -> Set[DirectImport]:
        """
        Parse `import x` statements
        """
        assert isinstance(node, ast.Import)

        imported_mods: Set[DirectImport] = set()

        for alias in node.names:
            mod_name = ModName.from_str(alias.name)

            try:
                imported_mods.add(
                    DirectImport(
                        mod_name=mod_name,
                        path=mod_name.file_path,
                        lineno=node.lineno,
                        col_offset=node.col_offset,
                    )
                )
            except ModuleNotFound:
                logger.warning(f"Could not find {mod_name} module. Could be an optional import. Skipping it")
                continue

        return imported_mods


class ImportFromParser:
    def __init__(self) -> None:
        ...

    def __call__(self, mod_name: ModName, node: ast.AST) -> Set[DirectImport]:
        """
        Parse `from x import ...` statements
        """
        assert isinstance(node, ast.ImportFrom)

        imported_modules: Set[DirectImport] = set()

        base_module: List[str] = []

        if node.level == 0:
            base_module = ModName.split(node.module)

        if node.level >= 1:
            level_up = node.level

            try:
                if mod_name.is_package:
                    level_up -= 1
            except ModuleNotFound:
                return set()

            base_module = [*mod_name.resolve(level_up).parts]

            if node.module:
                # could be none in case of `from . import Field`
                base_module.append(node.module)

        for alias in node.names:
            obj_path = [*base_module, alias.name]

            logger.debug(f"Analyzing {ModName.join(obj_path)} import")

            try:
                mod_name, obj = ModName.from_object_path(obj_path)

                logger.debug(f"- {mod_name}, obj: {obj}")

                imported_modules.add(
                    DirectImport(
                        mod_name=mod_name,
                        path=mod_name.file_path,
                        lineno=node.lineno,
                        col_offset=node.col_offset,
                    )
                )
            except ModuleNotFound:
                logger.warning(
                    f"Could not find {ModName.join(obj_path)} module. Could be an optional import. Skipping it"
                )
                continue

        return imported_modules


class ModParser:
    def __init__(self) -> None:
        self._parsers: Dict[Any, Parser] = {
            ast.Import: ImportParser(),
            ast.ImportFrom: ImportFromParser(),
        }

    def parse(self, module_name: ModName, content: str) -> Set[DirectImport]:
        try:
            ast_tree = ast.parse(content)
        except SyntaxError:
            raise

        imported_mods: Set[DirectImport] = set()

        for node in ast.walk(ast_tree):
            for node_class, node_parser in self._parsers.items():
                if isinstance(node, node_class):
                    imported_mods |= node_parser(module_name, node)
                    continue

        return imported_mods
