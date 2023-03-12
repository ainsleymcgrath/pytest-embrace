"""Assemble a test schema that includes mutable things.
Create 2 modules that implement it.
Module A imports `some_mutable_thing` from Module B and messes with it.
Verify that mutations during run of A do not spill over into B."""

from __future__ import annotations

import pytest

from tests.test_plugin.utils import make_autouse_conftest, make_test_run_outcome_fixture

_ = make_autouse_conftest(
    """
        from dataclasses import dataclass
        from typing import Dict, List
        from pytest_embrace import Embrace


        @dataclass
        class MutableCase:
            mut: Dict[str, int]


        mut_config = Embrace(MutableCase)


        @mut_config.fixture
        def mut_case(case: MutableCase):
            return None
        """
)


outcome = make_test_run_outcome_fixture(
    test_first="""
        mut = {"foo": 1}


        def test(mut_case):
            assert mut_case.case.mut == {"foo": 1}
        """,
    test_second="""
        from test_first import mut

        mut['bar'] = 6


        def test(mut_case):
            assert mut_case.case.mut == {"foo": 1, "bar": 6}
        """,
)


def test(outcome: pytest.RunResult) -> None:
    outcome.assert_outcomes(passed=2)
