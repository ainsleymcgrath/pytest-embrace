from dataclasses import dataclass

import pytest

from pytest_embrace.exc import CaseConfigurationError
from pytest_embrace.loader import ModuleInfo, load

from .utils import module_factory


@dataclass
class ValidCase:
    attr1: str
    attr2: str
    attr3: int


def test_load_attributes() -> None:
    mod = module_factory(attr1="hey", attr2="hello", attr3=444)
    (loaded,) = load(ModuleInfo(case_type=ValidCase, module=mod))
    assert loaded == ValidCase("hey", "hello", 444)


def test_load_fail_on_missing() -> None:
    mod = module_factory(attr1="yo")
    with pytest.raises(
        CaseConfigurationError, match="Only got attributes {'attr1': 'yo'}"
    ):
        load(ModuleInfo(case_type=ValidCase, module=mod))
