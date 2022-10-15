from __future__ import annotations

from dataclasses import dataclass

import pytest

from pytest_embrace.exc import CaseConfigurationError
from pytest_embrace.loader import load
from tests.conftest import ModuleInfoFactory


@dataclass
class ValidCase:
    attr1: str
    attr2: str
    attr3: int


def test_load_attributes(module_info_factory: ModuleInfoFactory) -> None:
    target = module_info_factory.build(ValidCase, attr1="hey", attr2="hello", attr3=444)
    (loaded,) = load(target)
    assert loaded == ValidCase("hey", "hello", 444)


def test_load_fail_on_missing(module_info_factory: ModuleInfoFactory) -> None:
    target = module_info_factory.build(ValidCase, attr1="yo")
    with pytest.raises(
        CaseConfigurationError, match="Only got attributes {'attr1': 'yo'}"
    ):
        load(target)
