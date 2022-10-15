from __future__ import annotations

from dataclasses import dataclass

from pytest_embrace.case import trickles
from pytest_embrace.codegen import CaseRender
from tests.conftest import ValidPythonAssertion
from tests.test_codegen.conftest import make_renderer_fixture


@dataclass
class TableCase:
    bottom: float = 0
    top: float = trickles()


CaseRenderUnderTest = CaseRender[TableCase]


renderer = make_renderer_fixture(TableCase, fixture_name="table")


def test_table_only(
    assert_valid_text_is: ValidPythonAssertion, renderer: CaseRenderUnderTest
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


def test_table_and_module_level_attrs(
    assert_valid_text_is: ValidPythonAssertion, renderer: CaseRenderUnderTest
) -> None:
    """Handle the case where you want to render trickle-down attrs + `table`."""
    mixed_values = (
        TableCase(top=1),
        [
            TableCase(bottom=11.1),
            TableCase(bottom=4.0, top=99.9),
        ],
    )
    assert_valid_text_is(
        renderer.with_values(mixed_values),
        """
        from pytest_embrace import CaseArtifact
        from tests.test_codegen.test_render_table_case import TableCase

        top = 1

        table = [
            TableCase(bottom=11.1),
            TableCase(bottom=4.0, top=99.9),
        ]


        def test(table: CaseArtifact[TableCase]) -> None:
            ...
        """,
    )
