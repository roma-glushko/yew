from pathlib import Path

import pytest

from tests import FIXTURE_DIR
from yew.collection import ModName


def test__modname_hashable() -> None:
    modname1 = ModName.from_str("common.filesystems.async")
    modname2 = ModName.from_str("common.filesystems.async")
    modname3 = ModName.from_str("common.filesystems.windows")

    assert modname1 == modname2
    assert modname1 != modname3
    assert modname2 != modname3

    mod_set: set[ModName] = set()
    mod_set.add(modname1)

    assert modname2 in mod_set
    assert modname3 not in mod_set


@pytest.mark.parametrize(
    "path,module_name",
    [
        (FIXTURE_DIR / "relative_imports" / "fields" / "json.py", "tests.fixtures.relative_imports.fields.json"),
    ],
)
def test__modname__from_path(path: Path, module_name: str) -> None:
    assert module_name == str(ModName.from_path(path))
