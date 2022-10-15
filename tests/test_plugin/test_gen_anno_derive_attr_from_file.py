from __future__ import annotations

import pytest

from tests.test_plugin.utils import make_autouse_conftest

_ = make_autouse_conftest(
    """
import sys

from dataclasses import dataclass

from pytest_embrace import Embrace, derive_from_filename


@dataclass
class AnnotatedCase:
    horse_type: str = derive_from_filename()


embrace_1 = Embrace(AnnotatedCase)


@embrace_1.fixture
def horse_case(case: AnnotatedCase) -> None:
    assert case.horse_type == 'palomino'
"""
)


TEST_FILE = """
def test(horse_case):
    ...
"""


def test_success(pytester: pytest.Pytester) -> None:
    dir = pytester.mkpydir("test_nested")
    file = dir / "test_palomino.py"
    file.touch()
    with file.open("w") as f:
        f.write(TEST_FILE)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(passed=1)


def test_failure(pytester: pytest.Pytester) -> None:
    dir = pytester.mkpydir("test_nested")
    file = dir / "test_some_other_horse.py"
    file.touch()
    with file.open("w") as f:
        f.write(TEST_FILE)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(errors=1)
