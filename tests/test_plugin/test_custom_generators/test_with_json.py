from __future__ import annotations

import pytest

from ..utils import generated_module_stdout_factory, make_autouse_conftest

_ = make_autouse_conftest(
    """
from dataclasses import dataclass
import pytest

from pytest_embrace import Embrace
from pytest_embrace.case import CaseArtifact


@dataclass
class CoercionCase:
    number: int


embrace = Embrace(CoercionCase)


@embrace.fixture
def coercion_case(case: CoercionCase) -> None:
    pass


@embrace.generator
def gen(number: int):
    return CoercionCase(number=number)
"""
)


# @pytest.mark.xfail(reason="Type coercion not implemented :(")
def test_dynamic_name_generator(pytester: pytest.Pytester) -> None:
    outcome = pytester.runpytest("--embrace=coercion_case:gen number=4")
    outcome.stdout.fnmatch_lines(
        generated_module_stdout_factory(
            "number = 4",
            case_type="CoercionCase",
            fixture="coercion_case",
        ),
    )
