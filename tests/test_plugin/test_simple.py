import pytest

CONFTEST = """
from dataclasses import dataclass
import pytest

from pytest_embrace import  CaseRunner, Embrace
from pytest_embrace.case import CaseArtifact


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
    return {"backwards": [*reversed(case.name)]}


simple_case = embrace.caller_fixture_factory("simple_case")
            """

SINGLE_TEST_FILE = """
name = 'hey'

def test(simple_case):
    ...
"""

MULTI_TEST_FILE = """
from conftest import MyCase

table = [MyCase(name='hey'), MyCase(name='yo')]

def test(simple_case):
    ...
"""

USE_ARTIFACT_AFTER_FILE = """
from conftest import MyCase

name = 'hey'

def test(simple_case):
    assert simple_case.case.name == 'hey'
    assert simple_case.actual_result['backwards'] == ['y', 'e', 'h']
"""


@pytest.fixture(autouse=True)
def simple_case_conftest(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(CONFTEST)


def test_single(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(SINGLE_TEST_FILE)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(passed=1)


def test_multi(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(MULTI_TEST_FILE)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(passed=1, errors=1)


def test_use_artifact(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(USE_ARTIFACT_AFTER_FILE)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(passed=1, errors=0)
