from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import pytest

from pytest_embrace.codegen import CaseRender, RenderText
from pytest_embrace.exc import CodeGenError
from tests.conftest import ValidPythonAssertion
from tests.test_codegen.conftest import make_renderer_fixture


@dataclass
class UnserializeableCase:
    collection: set[str]
    subcase: "UnserializeableCase" | None = None
    funcdef: Callable[..., object] | None = None


CaseRenderUnderTest = CaseRender[UnserializeableCase]

renderer = make_renderer_fixture(UnserializeableCase, fixture_name="case")


def test_flat(
    assert_valid_text_is: ValidPythonAssertion, renderer: CaseRenderUnderTest
) -> None:
    values = UnserializeableCase(
        collection=RenderText('{"foo", "bar"}'),
        subcase=RenderText('UnserializeableCase({"haha"})'),
    )
    assert_valid_text_is(
        renderer.with_values(values, hinted=False),
        """
    from pytest_embrace import CaseArtifact
    from tests.test_codegen.test_render_render_custom_code import UnserializeableCase

    collection = {"foo", "bar"}
    subcase = UnserializeableCase({"haha"})


    def test(case: CaseArtifact[UnserializeableCase]) -> None:
        ...
        """,
    )


def test_render_function(
    assert_valid_text_is: ValidPythonAssertion, renderer: CaseRenderUnderTest
) -> None:
    """Cool one here. Demo special behavior for multi-line input & fuction defs."""
    values = UnserializeableCase(
        collection=RenderText("{}"),
        # this doesn't get rendered as an assignment
        funcdef=RenderText(
            """
            def funcdef(bar):
                return object()
            """
        ),
    )
    assert_valid_text_is(
        renderer.with_values(values, hinted=False),
        """
    from pytest_embrace import CaseArtifact
    from tests.test_codegen.test_render_render_custom_code import UnserializeableCase

    collection = {}


    def funcdef(bar):
        return object()


    def test(case: CaseArtifact[UnserializeableCase]) -> None:
        ...
        """,
    )


def test_render_function_name_mismatch(renderer: CaseRenderUnderTest) -> None:
    """Not allowed to define a function whose name doesn't match what's in the Case."""
    values = UnserializeableCase(
        collection=RenderText("{}"),
        funcdef=RenderText(
            """
            def uhoh(bar):
                return object()
            """
        ),
    )
    with pytest.raises(
        CodeGenError,
        match="Can't render function called 'uhoh' for arg 'funcdef'."
        " Rename the function to 'funcdef' and try again.",
    ):
        renderer.with_values(values, hinted=False),
