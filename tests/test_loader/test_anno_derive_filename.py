from dataclasses import dataclass
from typing import Annotated

from pytest_embrace import anno
from pytest_embrace.loader import from_module

from .utils import module_factory


@dataclass
class AnnotatedWithDeriveNameCase:
    magic_spell: Annotated[str, anno.DeriveNameFromFile()]


def test_get_name_from_file_default() -> None:
    mod = module_factory(name="my.tests.test_mage_hand")
    loaded = from_module(AnnotatedWithDeriveNameCase, mod)
    assert loaded.magic_spell == "mage_hand"
