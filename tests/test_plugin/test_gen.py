from __future__ import annotations

import pytest

from .utils import generated_module_stdout_factory, make_autouse_conftest

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
class MyCase1:
    name: str


embrace_1 = Embrace(MyCase1)


@embrace_1.fixture
def fix_1(case: MyCase1, fix: str) -> None:
    assert case.name == fix


@dataclass
class MyCase2:
    num: int
    foo: str


embrace_2 = Embrace(MyCase2)


@embrace_2.fixture
def fix_2(case: MyCase2, fix: str) -> None:
    assert len(case.num) >= len(fix)
    assert case.foo != 'papaya'"""
)


@pytest.mark.parametrize(
    "fixture_name, matchlines",
    [
        (
            "buzzz",
            # XXX maybe some leaky state? other fixtures are called out in this output
            # (thus the glob before fix_1)
            ["*No such fixture 'buzzz'. Your options are *'fix_1', 'fix_2'*"],
        ),
        (
            "fix_1",
            generated_module_stdout_factory(
                "name: str", fixture="fix_1", case_type="MyCase1"
            ),
        ),
        (
            "fix_2",
            generated_module_stdout_factory(
                "num: int", "foo: str", fixture="fix_2", case_type="MyCase2"
            ),
        ),
    ],
)
def test_gen_opt_can_find(
    fixture_name: str, matchlines: str, pytester: pytest.Pytester
) -> None:
    """Looking for the type hints that show up in generated modules."""
    outcome = pytester.runpytest(f"--embrace={fixture_name}")
    outcome.stdout.fnmatch_lines(matchlines, consecutive=True)
