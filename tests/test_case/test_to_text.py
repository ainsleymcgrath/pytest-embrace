import sys
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
        assert dedent(expected).lstrip("\n") == actual
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
    text = target.render_skeleton()
    assert_valid_text_is(
        text,
        """
        from pytest_embrace import CaseArtifact
        from tests.test_case.test_to_text import GlobalsCase

        x: float
        y: str


        def test(the_case: CaseArtifact[GlobalsCase]) -> None:
            ...
        """,
    )


@dataclass
class SomeCaseWithImports:
    foo: Callable[[deque], chain]


def test_to_text_builtins(assert_valid_text_is: AssertionHelper) -> None:

    target = CaseTypeInfo(SomeCaseWithImports, caller_name="the_case")
    assert_valid_text_is(
        target.render_skeleton(),
        """
        from collections import deque
        from collections.abc import Callable
        from itertools import chain

        from pytest_embrace import CaseArtifact
        from tests.test_case.test_to_text import SomeCaseWithImports

        foo: Callable[[deque], chain]


        def test(the_case: CaseArtifact[SomeCaseWithImports]) -> None:
            ...
        """
        if sys.version_info >= (3, 9)
        else (
            """
            from collections import deque
            from itertools import chain
            from typing import Callable

            from pytest_embrace import CaseArtifact
            from tests.test_case.test_to_text import SomeCaseWithImports

            foo: Callable[[deque], chain]


            def test(the_case: CaseArtifact[SomeCaseWithImports]) -> None:
                ...
            """
        ),
    )
