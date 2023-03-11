from __future__ import annotations

from dataclasses import dataclass

from pytest_embrace import RenderModuleBody, trickles
from pytest_embrace.codegen import CaseRender
from tests.conftest import ValidPythonAssertion
from tests.test_codegen.conftest import make_renderer_fixture


@dataclass
class ExpertCase:
    bottom: float
    top: float = trickles()


CaseRenderUnderTest = CaseRender[ExpertCase]


# @pytest.fixture
# def renderer(make_renderer: RendererMaker) -> CaseRender[ExpertCase]:
#     return make_renderer(ExpertCase, fixture_name="expert")


renderer = make_renderer_fixture(ExpertCase, fixture_name="expert")


def xtest_expert(
    assert_valid_text_is: ValidPythonAssertion, renderer: CaseRenderUnderTest
) -> None:
    assert_valid_text_is(
        renderer.with_values(
            RenderModuleBody(
                "# hehe begin w comment",
            )
        ),
        """
        from pytest_embrace import CaseArtifact
        from tests.test_codegen.test_render_expert import ExpertCase

        table = [
            TableCase(bottom=1.2, top=4.5),
            TableCase(bottom=4.0, top=99.9),
        ]


        def test(table: CaseArtifact[ExpertCase]) -> None:
            ...
        """,
    )
