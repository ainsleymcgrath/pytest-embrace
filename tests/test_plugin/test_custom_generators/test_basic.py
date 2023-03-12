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
class MyCase:
    name: str


embrace = Embrace(MyCase)


@embrace.fixture
def my_case(case: MyCase) -> None:
    pass


@embrace.generator
def dynamic_name(name: str):
    return MyCase(name=f"Dynamic {name.title()}!")
"""
)


def test_dynamic_name_generator(pytester: pytest.Pytester) -> None:
    outcome = pytester.runpytest("--embrace=my_case:dynamic_name name=pieRre")
    outcome.stdout.fnmatch_lines(
        generated_module_stdout_factory(
            'name = "Dynamic Pierre!"',
            case_type="MyCase",
            fixture="my_case",
        ),
    )
