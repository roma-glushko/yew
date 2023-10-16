import pytest

from tests import FIXTURE_DIR
from yew.collection import ModName
from yew.mods.parsers import ModParser


def test__mod_parser__syntax_error() -> None:
    parser = ModParser()

    with open(FIXTURE_DIR / "syntaxerrs" / "broken_class.py") as file:
        with pytest.raises(SyntaxError):
            parser.parse(ModName.from_str("tests.fixtures.syntaxerrs.broken_class"), content=file.read())
