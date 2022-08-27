"""Test an implementation of a fixture that yields.
Ensure that the cleanup after the yield happens."""
import pytest

from .utils import make_autouse_conftest, make_test_run_outcome_fixture

_ = make_autouse_conftest(
    """
         from dataclasses import dataclass
         import pytest

         from pytest_embrace import Embrace
         from pytest_embrace.case import CaseArtifact

         watcher = {"fix_yields_yielded": False, "runner_yielded": False}


         @pytest.fixture
         def fix_yields() -> str:
             print("hey")
             yield "hey"
             print("Cleaning up fixture")

         @dataclass
         class TheCase:
             name: str


         embrace = Embrace(TheCase)

         @embrace.register_case_runner
         def my_runner(case: TheCase, fix_yields: str) -> None:
             assert case.name == fix_yields
             yield "yoooo"
             print("Cleaning up runner")


         cleanup_case = embrace.caller_fixture_factory("cleanup_case")
         """
)

single_test_outcome = make_test_run_outcome_fixture(
    """
    from conftest import watcher
    name = "hey"

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
