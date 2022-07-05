from textwrap import dedent
from typing import Callable, List

import pytest

TestFuncWithPytester = Callable[[pytest.Pytester], None]


def make_conftest(text: str, *, autose: bool = False) -> TestFuncWithPytester:
    @pytest.fixture(autouse=autose)
    def autouse_conftest(pytester: pytest.Pytester) -> None:
        pytester.makeconftest(dedent(text))

    return autouse_conftest


def make_autouse_conftest(text: str) -> Callable[[pytest.Pytester], None]:
    return make_conftest(text, autose=True)


def generated_module_stdout_factory(
    *type_hints: str,
    fixture: str,
    case_type: str,
    imports: str = "from pytest_embrace import CaseArtifact",
    typical_table_kwargs: List[str] = None,
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
        "",
        *type_hints,
        *typical_table_kwargs,
        "",
        "",
        f"def test({fixture}: CaseArtifact[{case_type}]) -> None:",
        "    ...",
    ]
