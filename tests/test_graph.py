from collections import namedtuple

from tests import FIXTURE_DIR
from yew.mods.graph import build_mod_graph

ImportInfo = namedtuple("ImportInfo", ["imports", "imported_by"])


def test__parser__imports() -> None:
    modules: dict[str, ImportInfo] = {
        "tests.fixtures.imports": ImportInfo(1, 0),
        "tests.fixtures.imports.utils": ImportInfo(0, 1),
        "tests.fixtures.imports.fields": ImportInfo(0, 3),
        "tests.fixtures.imports.fields.json": ImportInfo(1, 0),
        "tests.fixtures.imports.fields.security": ImportInfo(1, 0),
        "tests.fixtures.imports.fields.security.password": ImportInfo(2, 1),
    }
    graph = build_mod_graph([FIXTURE_DIR / "imports"], workers=1)

    assert len(graph) == len(modules)

    for mod_name in modules:
        actual_module = graph[mod_name]
        expected_module = modules[mod_name]

        assert actual_module is not None

        assert len(actual_module.imports) == expected_module.imports
        assert len(actual_module.imported_by) == expected_module.imported_by
