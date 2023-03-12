from __future__ import annotations

import pytest

from tests.test_plugin.utils import make_autouse_conftest

_ = make_autouse_conftest(
    """

from dataclasses import dataclass

from pytest_embrace import Embrace, derive_from_filename, trickles


@dataclass
class DeriveAndTableCase:
    horse_name: str
    horse_type: str = derive_from_filename()
    horse_age: int = trickles()


mix_n_match = Embrace(DeriveAndTableCase)


@mix_n_match.fixture
def mix_n_match_case(case: DeriveAndTableCase) -> None:
    if case.horse_name == 'Willybilly':
        assert case.horse_age == 22
        return

    if case.horse_name == 'Jolene':
        assert case.horse_age == 33
        return
"""
)


TEST_FILE = """
from conftest import DeriveAndTableCase


horse_age = 22

table = [
    DeriveAndTableCase(horse_name='Willybilly'),
    DeriveAndTableCase(horse_name='Jolene', horse_age=33),
]


def test(mix_n_match_case):
    assert mix_n_match_case.case.horse_type == 'palomino'
"""


def test_success(pytester: pytest.Pytester) -> None:
    dir = pytester.mkpydir("test_nested")
    file = dir / "test_palomino.py"
    file.touch()
    with file.open("w") as f:
        f.write(TEST_FILE)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(passed=2)
