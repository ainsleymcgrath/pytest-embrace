from textwrap import dedent
import pytest


pytest_plugins = "pytester"


def test_idk(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(
        """
from dataclasses import dataclass
import pytest

from pytest_embrace import  CaseRunner, Embrace
from pytest_embrace.case import CaseArtifact


pytest_plugins = "pytest_embrace.plugin"


@pytest.fixture
def fix() -> str:
    return "hey"


@dataclass
class MyCase:
    name: str


embrace = Embrace(MyCase)


@embrace.register_case_runner
def my_runner(case: MyCase, fix: str) -> None:
    assert case.name == fix


simple_case = embrace.caller_fixture_factory("simple_case")
            """
    )

    pytester.makepyfile(
        dedent(
            """
        name = 'hey'

        def test(simple_case):
            ...
        """
        )
    )
    outcome = pytester.runpytest()
    print("\n".join(outcome.outlines))
    outcome.assert_outcomes(passed=1)
