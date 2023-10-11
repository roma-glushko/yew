import ast
import dataclasses
import tokenize
from pathlib import Path
from typing import Set


@dataclasses.dataclass(frozen=True)
class ImportReference:
    module_name: str
    lineno: int
    col_offset: int


class ImportParser:
    def __init__(self) -> None:
        ...

    def __call__(self, node: ast.AST) -> Set[ImportReference]:
        """
        Parse `import x` statements
        """
        assert isinstance(node, ast.Import)

        imported_modules: Set[ImportReference] = set()

        for alias in node.names:
            # TODO: Filter or process names if needed
            imported_modules.add(ImportReference(
                module_name=alias.name,
                lineno=node.lineno,
                col_offset=node.col_offset,
            ))

        return imported_modules


class ImportFromParser:
    def __init__(self) -> None:
        ...

    def __call__(self, node: ast.AST) -> Set[ImportReference]:
        """
        Parse `from x import ...` statements
        """
        assert isinstance(node, ast.ImportFrom)

        imported_modules: Set[ImportReference] = set()

        module_base: str = ""

        if node.level == 0:
            module_base = node.module

        if node.level >= 1:
            module_base = "{up}"  # TODO: retrieve this from context

        for alias in node.names:
            imported_module = ".".join([module_base, alias.name])

            imported_modules.add(ImportReference(
                module_name=imported_module,
                lineno=node.lineno,
                col_offset=node.col_offset,
            ))

        return imported_modules


class ModParser:
    def __init__(self) -> None:
        self._parsers = {
            ast.Import: ImportParser(),
            ast.ImportFrom: ImportFromParser(),
        }

    def parse(self, module_path: Path) -> Set[str]:
        with tokenize.open(module_path) as file:
            content = file.read()

        try:
            ast_tree = ast.parse(content)
        except SyntaxError as e:
            raise

        module_imports: Set[str] = set()

        for node in ast.walk(ast_tree):
            for node_class, node_parser in self._parsers.items():
                if isinstance(node, node_class):
                    module_imports |= node_parser(node)
                    continue

        return module_imports
