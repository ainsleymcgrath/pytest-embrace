import sys
from dataclasses import dataclass

import pytest

from pytest_embrace import derive_from_filename
from pytest_embrace.loader import load

from .utils import module_factory


@dataclass
class AnnotatedWithDeriveNameCase:
    magic_spell: str = derive_from_filename()


pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="get_type(Annotated[...]) returns nothing in 3.8"
    " so this feature can't work at all",
)


def test_get_name_from_file_default() -> None:
    mod = module_factory(name="my.tests.test_mage_hand")
    (loaded,) = load(AnnotatedWithDeriveNameCase, mod)
    assert loaded.magic_spell == "mage_hand"
