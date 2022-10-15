from __future__ import annotations

from dataclasses import dataclass, field

from pytest_embrace.codegen import CaseRender
from tests.conftest import ValidPythonAssertion
from tests.test_codegen.conftest import make_renderer_fixture


@dataclass
class Case:
    number: int
    word: str
    items: list[str] = field(default_factory=list)


CaseRenderUnderTest = CaseRender[Case]

renderer = make_renderer_fixture(Case, fixture_name="case")


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


def test_with_values_skips_defaults(
    assert_valid_text_is: ValidPythonAssertion, renderer: CaseRenderUnderTest
) -> None:
    values = Case(number=5, word="hello")  # when default is excluded, it never renders

    assert_valid_text_is(
        renderer.with_values(values),
        """
        from pytest_embrace import CaseArtifact
        from tests.test_codegen.test_render_flat_case import Case

        number: int = 5
        word: str = "hello"


        def test(case: CaseArtifact[Case]) -> None:
            ...
        """,
    )


def test_with_values_skips_defaults_even_when_passed(
    assert_valid_text_is: ValidPythonAssertion, renderer: CaseRenderUnderTest
) -> None:
    # empty items list is default
    # quirky, but it still won't render even though it was passed explicitly.
    values = Case(number=5, word="hello", items=[])

    assert_valid_text_is(
        renderer.with_values(values),
        """
        from pytest_embrace import CaseArtifact
        from tests.test_codegen.test_render_flat_case import Case

        number: int = 5
        word: str = "hello"


        def test(case: CaseArtifact[Case]) -> None:
            ...
        """,
    )
