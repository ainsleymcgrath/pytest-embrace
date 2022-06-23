import sys

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


@pytest.fixture
def annotated_case_conftest(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(CONFTEST)


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="get_type(Annotated[...]) returns nothing in 3.8"
    " so this feature can't work at all",
)
def test_comment_annotated_attr(
    pytester: pytest.Pytester, annotated_case_conftest: None
) -> None:
    outcome = pytester.runpytest("--embrace=anno_case")
    matchlines = matchable_fnlines_gen_output(
        "name: str  # This is ... the name.",
        fixture="anno_case",
        case_type="AnnotatedCase",
    )
    outcome.stdout.fnmatch_lines(matchlines, consecutive=True)
