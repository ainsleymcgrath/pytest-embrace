import pytest

from .utils import generated_module_stdout_factory, make_autouse_conftest

_ = make_autouse_conftest(
    """
from dataclasses import dataclass
import pytest

from pytest_embrace import Embrace
from pytest_embrace.case import CaseArtifact


@pytest.fixture
def fix() -> str:
    return "hey"


@dataclass
class MyCase1:
    name: str


embrace_1 = Embrace(MyCase1)


@embrace_1.register_case_runner
def my_runner_1(case: MyCase1, fix: str) -> None:
    assert case.name == fix


caller_1 = embrace_1.caller_fixture_factory("caller_1")


@dataclass
class MyCase2:
    num: int
    foo: str


embrace_2 = Embrace(MyCase2)


@embrace_2.register_case_runner
def my_runner_2(case: MyCase2, fix: str) -> None:
    assert len(case.num) >= len(fix)
    assert case.foo != 'papaya'


caller_2 = embrace_2.caller_fixture_factory("caller_2")
            """
)


@pytest.mark.parametrize(
    "caller_name, matchlines",
    [
        (
            "foo",
            ["*No such fixture 'foo'. Your options are ['caller_1', 'caller_2'*"],
        ),
        (
            "caller_1",
            generated_module_stdout_factory(
                "name: str", fixture="caller_1", case_type="MyCase1"
            ),
        ),
        (
            "caller_2",
            generated_module_stdout_factory(
                "num: int", "foo: str", fixture="caller_2", case_type="MyCase2"
            ),
        ),
    ],
)
def test_gen_opt_can_find(
    caller_name: str, matchlines: str, pytester: pytest.Pytester
) -> None:
    """Looking for the type hints that show up in generated modules."""
    outcome = pytester.runpytest(f"--embrace={caller_name}")
    outcome.stdout.fnmatch_lines(matchlines, consecutive=True)
