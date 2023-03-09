from __future__ import annotations

from textwrap import dedent
from typing import Any, Callable, List, Tuple

import pytest

TestFuncWithPytester = Callable[[pytest.Pytester], None]


def make_conftest(text: str, *, autose: bool = False) -> TestFuncWithPytester:
    @pytest.fixture(autouse=autose)
    def autouse_conftest(pytester: pytest.Pytester) -> None:
        pytester.makeconftest(dedent(text))

    return autouse_conftest


def make_autouse_conftest(text: str) -> Callable[[pytest.Pytester], None]:
    return make_conftest(text, autose=True)


def make_test_run_outcome_fixture(
    *args: Any, pytest_args: Tuple[Any, ...] = (), **kwargs: Any
) -> Callable[[pytest.Pytester], pytest.RunResult]:
    """For the common case of:
        creating a python file (or files)
        immediately running pytest,
        directly using the Outcome.
    If other fixtures or complex setup are needed, this is not for you.
    Kwargs become filenames with a .py added."""

    @pytest.fixture
    def fixture(pytester: pytest.Pytester) -> pytest.RunResult:
        pytester.makepyfile(*args, **kwargs)

        outcome = pytester.runpytest(*pytest_args)
        return outcome

    return fixture


def generated_module_stdout_factory(
    *type_hints: str,
    fixture: str,
    case_type: str,
    imports: str = "from pytest_embrace import CaseArtifact",
    typical_table_kwargs: List[str] | None = None,
) -> List[str]:

    typical_table_kwargs = (
        []
        if typical_table_kwargs is None
        else [
            "",
            "",
            "# table = [",
            f"#    {case_type}(",
            *[f"#        {kwarg}=..." for kwarg in typical_table_kwargs],
            "#     )",
            "# ]",
        ]
    )

    return [
        "Copying the following output to your clipboard:",
        "",
        *imports.split("\n"),
        "",
        f"from conftest import {case_type}",
        "",
        *type_hints,
        *typical_table_kwargs,
        "",
        "",
        f"def test({fixture}: CaseArtifact[{case_type}]) -> None:",
        "    ...",
    ]
