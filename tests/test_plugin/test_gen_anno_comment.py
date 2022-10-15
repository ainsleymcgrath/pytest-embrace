from __future__ import annotations

import sys

import pytest

from .utils import generated_module_stdout_factory, make_autouse_conftest

_ = make_autouse_conftest(
    """
import sys

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

from dataclasses import dataclass

from pytest_embrace import Embrace


@dataclass
class AnnotatedCase:
    name: Annotated[str, 'This is ... the name.']


embrace_1 = Embrace(AnnotatedCase)


@embrace_1.fixture
def anno_case(case: AnnotatedCase, fix: str) -> None:
    assert case.name == fix
"""
)


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="get_type(Annotated[...]) returns nothing in 3.8"
    " so this feature can't work at all",
)
def test_comment_annotated_attr(pytester: pytest.Pytester) -> None:
    outcome = pytester.runpytest("--embrace=anno_case")
    matchlines = generated_module_stdout_factory(
        "name: str  # This is ... the name.",
        fixture="anno_case",
        case_type="AnnotatedCase",
    )
    outcome.stdout.fnmatch_lines(matchlines, consecutive=True)
