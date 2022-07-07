from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pytest

from pytest_embrace.exc import CaseConfigurationError
from pytest_embrace.loader import load
from tests.conftest import ModuleInfoFactory


@dataclass
class BuiltinsAttrsCase:
    string: str
    integer: int
    dictionary: Dict[str, str]


def test_happy(module_info_factory: ModuleInfoFactory) -> None:
    target = module_info_factory.build(
        BuiltinsAttrsCase, string="string", integer=5, dictionary={}
    )
    (loaded,) = load(target)
    expected = BuiltinsAttrsCase(string="string", integer=5, dictionary={})
    assert expected == loaded


def test_multiple_wrong_types(module_info_factory: ModuleInfoFactory) -> None:
    target = module_info_factory.build(
        BuiltinsAttrsCase, string="string", integer={}, dictionary=["nope."]
    )
    with pytest.raises(CaseConfigurationError, match="2 invalid attr values"):
        load(target)


def test_table_wrong_types(module_info_factory: ModuleInfoFactory) -> None:
    target = module_info_factory.build(
        BuiltinsAttrsCase,
        foo=["hey", "sup"],
        table=[
            BuiltinsAttrsCase(string="string", integer=5, dictionary={}),
            BuiltinsAttrsCase(string=555.555, integer=1, dictionary={}),  # type: ignore
        ],
    )
    with pytest.raises(CaseConfigurationError):
        load(target)
