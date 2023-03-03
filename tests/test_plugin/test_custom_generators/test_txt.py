"""Test usage of the `txt()` helper."""

import pytest

from ..utils import generated_module_stdout_factory, make_autouse_conftest

_ = make_autouse_conftest(
    """
from dataclasses import dataclass
import pytest

from pytest_embrace import Embrace, txt
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
        stuff=txt(f"stuff = ({inner_tuple})")
    )
"""
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
