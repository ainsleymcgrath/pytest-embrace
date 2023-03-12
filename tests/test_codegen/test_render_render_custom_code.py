from __future__ import annotations

from dataclasses import dataclass

from pytest_embrace.codegen import CaseRender, RenderText
from tests.conftest import ValidPythonAssertion
from tests.test_codegen.conftest import make_renderer_fixture


@dataclass
class UnserializeableCase:
    collection: set[str]
    subcase: "UnserializeableCase" | None = None


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
