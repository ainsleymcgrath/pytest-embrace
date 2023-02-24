import pytest

from .utils import generated_module_stdout_factory, make_autouse_conftest

_ = make_autouse_conftest(
    """
from dataclasses import dataclass
import pytest

from pytest_embrace import Embrace
from pytest_embrace.case import CaseArtifact


@pytest.fixture
def fix() -> str:
    return "hey"


@dataclass
class MyCase:
    name: str


embrace = Embrace(MyCase)


@embrace.fixture
def simple_case(case: MyCase, fix: str) -> None:
    pass


@embrace.generator
def dynamic_name(name: str):
    return MyCase(name=f"Dynamic {name.title()}!")
"""
)


def test_dynamic_name_generator(pytester: pytest.Pytester) -> None:
    outcome = pytester.runpytest("--embrace-gen=simple_case:dynamic_name name=pierre")
    outcome.stdout.fnmatch_lines(
        generated_module_stdout_factory(
            'name: str = "Dynamic Pierre!"',
            case_type="MyCase",
            fixture="simple_case",
        ),
    )
