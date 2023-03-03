from dataclasses import dataclass

from pytest_embrace.case import CaseTypeInfo
from pytest_embrace.codegen import CaseRender


@dataclass
class Case:
    number: int
    word: str
    items: list[str]


# def assert_valid_text_is


def xtest_skeleton() -> None:
    info = CaseTypeInfo(Case, fixture_name="case")
    renderer = CaseRender(info)
    assert renderer.skeleton() == "fart"
