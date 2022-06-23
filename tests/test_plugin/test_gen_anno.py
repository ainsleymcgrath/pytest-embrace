import pytest

from .utils import matchable_fnlines_gen_output

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
    name: Annotated[str, anno.Comment('This is ... the name.')]


embrace_1 = Embrace(AnnotatedCase)


@embrace_1.register_case_runner
def run(case: AnnotatedCase, fix: str) -> None:
    assert case.name == fix


anno_case = embrace_1.caller_fixture_factory("anno_case")
"""


@pytest.fixture(autouse=True)
def multiple_flavors_conftest(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(CONFTEST)


def test_gen_opt_can_find(pytester: pytest.Pytester) -> None:
    outcome = pytester.runpytest("--embrace=anno_case")
    matchlines = matchable_fnlines_gen_output(
        "name: str  # This is ... the name.",
        fixture="anno_case",
        case_type="AnnotatedCase",
    )
    outcome.stdout.fnmatch_lines(matchlines, consecutive=True)
