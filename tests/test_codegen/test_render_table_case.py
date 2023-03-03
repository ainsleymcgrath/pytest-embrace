from dataclasses import dataclass

import pytest

from pytest_embrace.case import trickles
from pytest_embrace.codegen import CaseRender
from tests.conftest import AssertionHelper
from tests.test_codegen.conftest import RendererMaker


@dataclass
class TableCase:
    bottom: float
    top: float = trickles()


CaseRenderUnderTest = CaseRender[TableCase]


@pytest.fixture
def renderer(make_renderer: RendererMaker) -> CaseRender[TableCase]:
    return make_renderer(TableCase, fixture_name="table")


def test_table_only(
    assert_valid_text_is: AssertionHelper, renderer: CaseRenderUnderTest
) -> None:
    assert_valid_text_is(
        renderer.with_values(
            [
                TableCase(bottom=1.2, top=4.5),
                TableCase(bottom=4.0, top=99.9),
            ]
        ),
        """
        from pytest_embrace import CaseArtifact
        from tests.test_codegen.test_render_table_case import TableCase

        table = [
            TableCase(bottom=1.2, top=4.5),
            TableCase(bottom=4.0, top=99.9),
        ]


        def test(table: CaseArtifact[TableCase]) -> None:
            ...
        """,
    )
