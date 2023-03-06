from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from pytest_embrace import derive_from_filename
from pytest_embrace.loader import load
from tests.conftest import ModuleInfoFactory


@dataclass
class AnnotatedWithDeriveNameCase:
    magic_spell: str = derive_from_filename()


def test_get_name_from_file_default(module_info_factory: ModuleInfoFactory) -> None:
    target = module_info_factory.build(
        AnnotatedWithDeriveNameCase, __name__="my.tests.test_mage_hand"
    )
    (loaded,) = load(target)
    assert loaded.magic_spell == "mage_hand"


class SomeNamesmace:
    def cool_stuff(self) -> str:
        return "cool"


ns = SomeNamesmace()


@dataclass
class DeriveWithParserCase:
    stuff: Callable = derive_from_filename(parse=lambda x: getattr(ns, x))


def test_get_name_from_file_with_parser(module_info_factory: ModuleInfoFactory) -> None:
    target = module_info_factory.build(DeriveWithParserCase, __name__="test_cool_stuff")
    (loaded,) = load(target)
    assert loaded.stuff() == "cool"
