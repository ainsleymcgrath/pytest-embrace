from collections import deque
from dataclasses import dataclass
from itertools import chain
from textwrap import dedent
from typing import Callable

import pytest

from pytest_embrace.case import CaseTypeInfo

AssertionHelper = Callable[[str, str], None]


@pytest.fixture
def assert_valid_text_is() -> AssertionHelper:
    def do_assert(actual: str, expected: str) -> None:
        assert dedent(expected) == actual
        try:
            exec(actual, globals(), locals())  # check that it's valid
        except Exception as e:
            raise pytest.fail(f"Invalid python generated: {actual}") from e

    return do_assert


@dataclass
class GlobalsCase:
    x: float
    y: str


def test_to_text_globals(assert_valid_text_is: AssertionHelper) -> None:

    target = CaseTypeInfo(GlobalsCase, caller_name="the_case")
    text = target.to_text()
    assert_valid_text_is(
        text,
        """
        from pytest_embrace import CaseArtifact

        from tests.test_case.test_to_text import GlobalsCase


        x: float
        y: str


        def test(the_case: CaseArtifact[GlobalsCase]) -> None:
            ...""",
    )


@pytest.mark.xfail("Not implemented!")
def test_to_text_builtins(assert_valid_text_is: AssertionHelper) -> None:
    @dataclass
    class Case:
        foo: Callable[[deque], chain]

    target = CaseTypeInfo(Case, caller_name="the_case")
    assert_valid_text_is(
        target.to_text(),
        """
        from collections import deque
        from itertools import chain
        from typing import Callable

        from pytest_embrace import CaseArtifact

        from tests.test_case.test_to_text import Case


        foo: Callable[[deque], chain]


        def test(the_case: CaseArtifact[Case]) -> None:
            ...""",
    )
