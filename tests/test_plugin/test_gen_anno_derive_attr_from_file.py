import sys

import pytest

CONFTEST = """
import sys

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

from dataclasses import dataclass

from pytest_embrace import CaseRunner, Embrace, anno


@dataclass
class AnnotatedCase:
    horse_type: Annotated[str, anno.DeriveNameFromFile()]


embrace_1 = Embrace(AnnotatedCase)


@embrace_1.register_case_runner
def run(case: AnnotatedCase) -> None:
    assert case.horse_type == 'palomino'


horse_case = embrace_1.caller_fixture_factory("horse_case")
"""


@pytest.fixture(autouse=True)
def annotated_case_conftest(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(CONFTEST)


TEST_FILE = """
def test(horse_case):
    ...
"""


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="get_type(Annotated[...]) returns nothing in 3.8"
    " so this feature can't work at all",
)
def test_success(pytester: pytest.Pytester) -> None:
    dir = pytester.mkpydir("test_nested")
    file = dir / "test_palomino.py"
    file.touch()
    with file.open("w") as f:
        f.write(TEST_FILE)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(passed=1)


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="get_type(Annotated[...]) returns nothing in 3.8"
    " so this feature can't work at all",
)
def test_failure(pytester: pytest.Pytester) -> None:
    dir = pytester.mkpydir("test_nested")
    file = dir / "test_some_other_horse.py"
    file.touch()
    with file.open("w") as f:
        f.write(TEST_FILE)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(errors=1)
