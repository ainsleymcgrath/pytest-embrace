from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from pytest_embrace.codegen import CaseRender
from tests.conftest import ValidPythonAssertion
from tests.test_codegen.conftest import RendererMaker


@dataclass
class Case:
    number: int
    word: str
    items: list[str] = field(default_factory=list)


CaseRenderUnderTest = CaseRender[Case]


@pytest.fixture
def renderer(make_renderer: RendererMaker) -> CaseRender[Case]:
    return make_renderer(Case, fixture_name="case")


def test_skeleton(
    assert_valid_text_is: ValidPythonAssertion, renderer: CaseRenderUnderTest
) -> None:
    assert_valid_text_is(
        renderer.skeleton(),
        """
        from pytest_embrace import CaseArtifact
        from tests.test_codegen.test_render_flat_case import Case

        number: int
        word: str
        items: list[str]


        def test(case: CaseArtifact[Case]) -> None:
            ...
        """,
    )


def test_with_values(
    assert_valid_text_is: ValidPythonAssertion, renderer: CaseRenderUnderTest
) -> None:
    values = Case(number=5, word="hello", items=["yo"])
    assert_valid_text_is(
        renderer.with_values(values),
        """
        from pytest_embrace import CaseArtifact
        from tests.test_codegen.test_render_flat_case import Case

        number: int = 5
        word: str = "hello"
        items: list[str] = ["yo"]


        def test(case: CaseArtifact[Case]) -> None:
            ...
        """,
    )
