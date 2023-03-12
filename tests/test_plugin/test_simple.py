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
         def fix() -> str:
             return "hey"


         @dataclass
         class MyCase:
             name: str


         embrace = Embrace(MyCase)


         @embrace.fixture
         def simple_case(case: MyCase, fix: str) -> None:
             assert case.name == fix
             return {"backwards": [*reversed(case.name)]}
         """
)

single_test_outcome = make_test_run_outcome_fixture(
    """
    name = 'hey'

    def test(simple_case):
        ..."""
)


def test_single(single_test_outcome: pytest.RunResult) -> None:
    single_test_outcome.assert_outcomes(passed=1)


table_test_outcome = make_test_run_outcome_fixture(
    """
    from conftest import MyCase

    table = [MyCase(name='hey'), MyCase(name='yo')]

    def test(simple_case):
        ..."""
)


def test_multi(table_test_outcome: pytest.RunResult) -> None:
    table_test_outcome.assert_outcomes(passed=1, errors=1)


artifact_usage_outcome = make_test_run_outcome_fixture(
    """
    from conftest import MyCase

    name = 'hey'

    def test(simple_case):
        assert simple_case.case.name == 'hey'
        assert simple_case.actual_result['backwards'] == ['y', 'e', 'h']"""
)


def test_use_artifact(artifact_usage_outcome: pytest.RunResult) -> None:
    artifact_usage_outcome.assert_outcomes(passed=1, errors=0)


artifact_plus_fixture_outcome = make_test_run_outcome_fixture(
    """
    from conftest import MyCase

    name = 'hey'

    def test(simple_case, fix):
        assert simple_case.actual_result['backwards'] == list(reversed(fix))"""
)


def test_use_artifact_plus_other(
    artifact_plus_fixture_outcome: pytest.RunResult,
) -> None:
    artifact_plus_fixture_outcome.assert_outcomes(passed=1, errors=0)
