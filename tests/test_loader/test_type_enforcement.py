from dataclasses import dataclass

import pytest

from pytest_embrace.exc import CaseConfigurationError
from pytest_embrace.loader import from_module

from .utils import module_factory


@dataclass
class BuiltinsAttrsCase:
    string: str
    integer: int
    dictionary: dict[str, str]


def test_happy() -> None:
    mod = module_factory(string="string", integer=5, dictionary={})
    loaded = from_module(BuiltinsAttrsCase, mod)
    expected = BuiltinsAttrsCase(string="string", integer=5, dictionary={})
    assert expected == loaded


def test_multiple_wrong_types() -> None:
    mod = module_factory(string="string", integer={}, dictionary=["nope."])
    with pytest.raises(CaseConfigurationError, match="2 invalid attr values"):
        from_module(BuiltinsAttrsCase, mod)
