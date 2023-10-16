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
        (FIXTURE_DIR / "imports" / "fields" / "json.py", "tests.fixtures.imports.fields.json"),
        (FIXTURE_DIR / "imports" / "fields" / "__init__.py", "tests.fixtures.imports.fields"),
        (
            FIXTURE_DIR / "imports" / "fields" / "security" / "password.py",
            "tests.fixtures.imports.fields.security.password",
        ),
    ],
)
def test__modname__from_path(path: Path, module_name: str) -> None:
    assert str(ModName.from_path(path)) == module_name


@pytest.mark.parametrize(
    "mod_name, expected_mod_name, expected_object_name",
    [
        (
            ["tests", "fixtures", "imports", "fields", "security", "password", "PasswordField"],
            "tests.fixtures.imports.fields.security.password",
            "PasswordField",
        ),
        (
            ["tests", "fixtures", "imports", "fields", "security", "password"],
            "tests.fixtures.imports.fields.security.password",
            None,
        ),
    ],
)
def test__modname__from_object_path(
    mod_name: list[str], expected_mod_name: str, expected_object_name: str | None
) -> None:
    actual_mod_name, actual_obj_path = ModName.from_object_path(mod_name)

    assert str(actual_mod_name) == expected_mod_name
    assert actual_obj_path == expected_object_name
