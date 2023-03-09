# skip the future import because it breaks dataclass.fields()
# and turns each Field.type to a string!
# isort: dont-add-import: from __future__ import annotations

import sys
from collections import deque
from dataclasses import dataclass
from itertools import chain
from typing import Callable

from pytest_embrace.case import CaseTypeInfo
from pytest_embrace.codegen import CaseRender
from tests.conftest import ValidPythonAssertion


@dataclass
class GlobalsCase:
    x: float
    y: str


def test_to_text_globals(assert_valid_text_is: ValidPythonAssertion) -> None:

    target = CaseRender(CaseTypeInfo(GlobalsCase, fixture_name="the_case"))
    text = target.skeleton()
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


def test_to_text_builtins(assert_valid_text_is: ValidPythonAssertion) -> None:

    target = CaseRender(CaseTypeInfo(SomeCaseWithImports, fixture_name="the_case"))
    assert_valid_text_is(
        target.skeleton(),
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
