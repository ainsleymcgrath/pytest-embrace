from __future__ import annotations

import pytest

from .utils import make_autouse_conftest, make_test_run_outcome_fixture

_ = make_autouse_conftest(
    """
     from __future__ import annotations
     from dataclasses import dataclass
     from pytest_embrace import Embrace

     @dataclass
     class RecursiveCase:
         again: RecursiveCase | None = None


     embrace = Embrace(RecursiveCase)


     @embrace.fixture
     def recur(case: RecursiveCase) -> None:
         assert 1


     # this one will be fine
     @dataclass
     class RecursiveCase2:
         again: RecursiveCase2 | None = None


     embrace2 = Embrace(RecursiveCase2, skip_validation=True)


     @embrace2.fixture
     def recur2(case: RecursiveCase2) -> None:
         assert 1
     """
)


avoidable_failure_outcome = make_test_run_outcome_fixture(
    """
    from conftest import RecursiveCase

    again = RecursiveCase()

    def test(recur):
        ..."""
)


def test_get_warned(avoidable_failure_outcome: pytest.RunResult) -> None:
    avoidable_failure_outcome.assert_outcomes(passed=0, errors=1)
    assert (
        "Set `skip_validation=True` in your Embrace()"
        in avoidable_failure_outcome.stdout.str()
    )


disabled_validation_outcome = make_test_run_outcome_fixture(
    """
    from conftest import RecursiveCase2

    again = RecursiveCase2()

    def test(recur2):
        ..."""
)


def test_disable_error(disabled_validation_outcome: pytest.RunResult) -> None:
    disabled_validation_outcome.assert_outcomes(passed=1, errors=0)
