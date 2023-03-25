from __future__ import annotations

from dataclasses import dataclass

import pytest

from pytest_embrace.exc import CaseConfigurationError
from pytest_embrace.loader import load
from tests.conftest import ModuleInfoFactory


@dataclass
class RecursiveCase:
    again: RecursiveCase | None = None


def test_error(module_info_factory: ModuleInfoFactory) -> None:
    target = module_info_factory.build(
        RecursiveCase, again=RecursiveCase(), __name__="ouchie"
    )

    with pytest.raises(CaseConfigurationError, match="ouchie.*' is recursive"):
        load(target)


def test_silence_error(module_info_factory: ModuleInfoFactory) -> None:
    target = module_info_factory.build(RecursiveCase, again=RecursiveCase())
    target.case.skip_validation = True

    (loaded,) = load(target)
    expected = RecursiveCase(again=RecursiveCase())
    assert expected == loaded
