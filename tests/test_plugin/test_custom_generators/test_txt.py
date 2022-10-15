"""Test usage of the `Render()` helper."""
# skip the future import because it breaks dataclass.fields()
# and turns each Field.type to a string!
# isort: dont-add-import: from __future__ import annotations


from __future__ import annotations

import pytest
from pyperclip import sys

from ..utils import generated_module_stdout_factory, make_autouse_conftest

_ = make_autouse_conftest(
    """
from dataclasses import dataclass
import pytest

from pytest_embrace import Embrace, RenderText
from pytest_embrace.case import CaseArtifact


@dataclass
class GreatCase:
    stuff: tuple[int, ...]


embrace = Embrace(GreatCase)


@embrace.fixture
def great(case: GreatCase) -> None:
    pass


@embrace.generator
def gen(how_many: int):
    items = range(how_many)
    inner_tuple = ", ".join(map(str, items))
    return GreatCase(
        stuff=RenderText(f"({inner_tuple})")
    )
"""
)


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="""Many difficulties after adding __future__ imports across the codebase.
    3.8 support is an increasingly low priority, so not bothering with extra logic
    to handle that in this test.""",
)
def test(pytester: pytest.Pytester) -> None:
    outcome = pytester.runpytest("--embrace=great:gen how_many=4")
    outcome.stdout.fnmatch_lines(
        generated_module_stdout_factory(
            "stuff = (0, 1, 2, 3)",
            case_type="GreatCase",
            fixture="great",
        ),
    )
