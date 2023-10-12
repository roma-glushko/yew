import ast
import tokenize
from pathlib import Path
from typing import Set

from yew.collections import DirectImport, ModName


class ImportParser:
    def __init__(self) -> None:
        ...

    def __call__(self, node: ast.AST) -> Set[DirectImport]:
        """
        Parse `import x` statements
        """
        assert isinstance(node, ast.Import)

        imported_mods: Set[DirectImport] = set()

        for alias in node.names:
            mod_name = ModName.from_str(alias.name)

            imported_mods.add(
                DirectImport(
                    mod_name=mod_name,
                    path=mod_name.file_path,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                )
            )

        return imported_mods


class ImportFromParser:
    def __init__(self) -> None:
        ...

    def __call__(self, node: ast.AST) -> Set[DirectImport]:
        """
        Parse `from x import ...` statements
        """
        assert isinstance(node, ast.ImportFrom)

        imported_modules: Set[DirectImport] = set()

        base_module: str = ""

        if node.level == 0:
            base_module = node.module

        if node.level >= 1:
            base_module = "services.users." + node.module  # TODO: retrieve this from context

        for alias in node.names:
            mod_name, _ = ModName.from_object_path([base_module, alias.name])

            imported_modules.add(
                DirectImport(
                    mod_name=mod_name,
                    path=mod_name.file_path,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                )
            )

        return imported_modules


class ModParser:
    def __init__(self) -> None:
        self._parsers = {
            ast.Import: ImportParser(),
            ast.ImportFrom: ImportFromParser(),
        }

    def parse(self, module_path: Path) -> Set[DirectImport]:
        with tokenize.open(module_path) as file:
            content = file.read()

        try:
            ast_tree = ast.parse(content)
        except SyntaxError:
            raise

        imported_mods: Set[DirectImport] = set()

        for node in ast.walk(ast_tree):
            for node_class, node_parser in self._parsers.items():
                if isinstance(node, node_class):
                    imported_mods |= node_parser(node)
                    continue

        return imported_mods
