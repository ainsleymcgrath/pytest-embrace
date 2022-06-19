import pytest

# # from pytest_embrace import Case, CaseRunner, Embrace
# # from pytest_embrace.case import CaseArtifact


# class MyCase(Case):
#     name: str

#     def testid(self) -> str:
#         return f"Testing -> {self.name}"


# @pytest.fixture
# def fix() -> str:
#     return "hey"


# e = Embrace(MyCase)


# @e.register_case_runner
# def my_runner(case: MyCase, fix: str) -> tuple[MyCase, str]:
#     assert case.name == fix


# simple_case = e.caller_fixture_factory("simple_case")
