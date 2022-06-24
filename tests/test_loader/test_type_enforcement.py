from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pytest

from pytest_embrace.exc import CaseConfigurationError
from pytest_embrace.loader import from_module, from_trickling_module

from .utils import module_factory


@dataclass
class BuiltinsAttrsCase:
    string: str
    integer: int
    dictionary: Dict[str, str]


def test_happy() -> None:
    mod = module_factory(string="string", integer=5, dictionary={})
    loaded = from_module(BuiltinsAttrsCase, mod)
    expected = BuiltinsAttrsCase(string="string", integer=5, dictionary={})
    assert expected == loaded


def test_multiple_wrong_types() -> None:
    mod = module_factory(string="string", integer={}, dictionary=["nope."])
    with pytest.raises(CaseConfigurationError, match="2 invalid attr values"):
        from_module(BuiltinsAttrsCase, mod)


def test_table_wrong_types() -> None:
    mod = module_factory(
        foo=["hey", "sup"],
        table=[
            BuiltinsAttrsCase(string="string", integer=5, dictionary={}),
            BuiltinsAttrsCase(string=555.555, integer=1, dictionary={}),  # type: ignore
        ],
    )
    with pytest.raises(CaseConfigurationError):
        from_trickling_module(BuiltinsAttrsCase, mod)
