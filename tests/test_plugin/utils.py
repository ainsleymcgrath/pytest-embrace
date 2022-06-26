from typing import List


def matchable_fnlines_gen_output(
    *type_hints: str,
    fixture: str,
    case_type: str,
    imports: str = "from pytest_embrace import CaseArtifact",
) -> List[str]:
    return [
        "Copying the following output to your clipboard:",
        "",
        *imports.split("\n"),
        "",
        f"from {case_type} import conftest" "",
        "",
        "",
        *type_hints,
        "",
        "",
        f"def test({fixture}: CaseArtifact[{case_type}]) -> None:",
        "    ...",
    ]
