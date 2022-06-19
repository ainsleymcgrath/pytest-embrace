from functools import partial
from inspect import signature
import logging
from typing import Callable, ClassVar, Generic, ParamSpec, Type

import pytest
from _pytest.fixtures import FixtureFunction

from .case import OneTimeOnlyMapping, CaseRunner, from_module
from .exc import EmbraceError


from .case import CaseType


logger = logging.getLogger()


P = ParamSpec("P")


class Embrace(Generic[CaseType]):
    _runner_registry: ClassVar[OneTimeOnlyMapping] = OneTimeOnlyMapping()

    def __init__(self, case_type: Type[CaseType]):
        self.case_type = case_type
        self.wrapped_func: CaseRunner | None = None
        self.runner: partial | None = None

    def register_case_runner(self, func: CaseRunner) -> FixtureFunction:

        self.wrapped_func = func

        @pytest.fixture
        def run_case_fixture(request: pytest.FixtureRequest) -> Callable:
            sig = signature(func)
            kwargs = {
                name: request.getfixturevalue(name)
                for name, param in sig.parameters.items()
                if param.annotation != self.case_type
            }
            self.runner = partial(func, **kwargs)

            return self.runner

        return run_case_fixture

    def caller_fixture_factory(self, name: str) -> FixtureFunction:
        self.__class__._runner_registry[name] = self.case_type

        @pytest.fixture
        def caller_fixture(request: pytest.FixtureRequest, case: CaseType) -> None:
            assert self.wrapped_func is not None
            request.getfixturevalue(self.wrapped_func.__name__)
            self.runner(case)
            pass

        return caller_fixture


class EmbraceTestSetupError(EmbraceError):
    ...


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    registry = Embrace._runner_registry
    embracers = [name for name in metafunc.fixturenames if name in registry]

    if len(embracers) > 1:
        raise EmbraceError(f"Can't request multiple Embrace tests. Got {embracers}")

    if len(embracers) == 0:
        return

    (sut,) = embracers
    cls = registry[sut]
    case = from_module(cls, metafunc.module)
    cases = table if (table := getattr(case, "table", [])) != [] else [case]
    metafunc.parametrize("case", cases, ids=[str(c) for c in cases])
