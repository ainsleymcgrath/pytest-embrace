"""Test an implementation of a fixture that yields.
Ensure that the cleanup after the yield happens."""
from __future__ import annotations

import pytest

from .utils import make_autouse_conftest, make_test_run_outcome_fixture

_ = make_autouse_conftest(
    """
         from dataclasses import dataclass
         import pytest

         from pytest_embrace import Embrace
         from pytest_embrace.case import CaseArtifact


         @pytest.fixture
         def fix_yields() -> str:
             yield "Reginald"
             print("Cleaning up fixture")

         @dataclass
         class TheCase:
             name: str


         embrace = Embrace(TheCase)

         @embrace.fixture
         def cleanup_case(case: TheCase, fix_yields: str) -> None:
             assert case.name == fix_yields
             yield "yoooo"
             print("Cleaning up runner")
         """
)

single_test_outcome = make_test_run_outcome_fixture(
    """
    name = "Reginald"

    def test(cleanup_case):
        assert cleanup_case.actual_result == "yoooo"
        ...
    """,
    # '-s' is synonym for '--capture=no', causes print statements to render
    pytest_args=("-s",),
)


def test_cleanup_happens(single_test_outcome: pytest.RunResult) -> None:
    single_test_outcome.assert_outcomes(passed=1)
    output = single_test_outcome.stdout.str()
    assert "Cleaning up fixture" in output
    assert "Cleaning up runner" in output
