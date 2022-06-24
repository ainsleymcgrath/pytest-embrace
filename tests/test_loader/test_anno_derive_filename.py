import sys
from dataclasses import dataclass

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

import pytest

from pytest_embrace import anno
from pytest_embrace.loader import from_module

from .utils import module_factory


@dataclass
class AnnotatedWithDeriveNameCase:
    magic_spell: Annotated[str, anno.DeriveFromFileName()]


pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="get_type(Annotated[...]) returns nothing in 3.8"
    " so this feature can't work at all",
)


def test_get_name_from_file_default() -> None:
    mod = module_factory(name="my.tests.test_mage_hand")
    loaded = from_module(AnnotatedWithDeriveNameCase, mod)
    assert loaded.magic_spell == "mage_hand"
