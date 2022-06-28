from dataclasses import dataclass
from typing import Callable

from pytest_embrace import derive_from_filename
from pytest_embrace.loader import load

from .utils import module_factory


@dataclass
class AnnotatedWithDeriveNameCase:
    magic_spell: str = derive_from_filename()


def test_get_name_from_file_default() -> None:
    mod = module_factory(name="my.tests.test_mage_hand")
    (loaded,) = load(AnnotatedWithDeriveNameCase, mod)
    assert loaded.magic_spell == "mage_hand"


class SomeNamesmace:
    def cool_stuff(self) -> str:
        return "cool"


ns = SomeNamesmace()


@dataclass
class DeriveWithParserCase:
    stuff: Callable = derive_from_filename(parse=lambda x: getattr(ns, x))


def test_get_name_from_file_with_parser() -> None:
    mod = module_factory(name="test_cool_stuff")
    (loaded,) = load(DeriveWithParserCase, mod)
    assert loaded.stuff() == "cool"
