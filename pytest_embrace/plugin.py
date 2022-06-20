from __future__ import annotations

import logging
from functools import partial
from inspect import signature
from typing import Callable, ClassVar, Generic, Type

import pytest
from _pytest.fixtures import FixtureFunction

from .case import CaseRunner, CaseType, OneTimeOnlyMapping, from_module
from .exc import EmbraceError

logger = logging.getLogger()


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
            # calling `getfixturevalue` for the wrapped func gets `run_case_fixture`.
            # doing *that* assigns self.runner at the last possible moment
            request.getfixturevalue(self.wrapped_func.__name__)
            assert self.runner is not None
            self.runner(case)

        return caller_fixture


class EmbraceTestSetupError(EmbraceError):
    ...


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    registry = Embrace._runner_registry
    embracers = [name for name in metafunc.fixturenames if name in registry]

    if len(embracers) > 1:
        raise EmbraceError(f"Can't request multiple Embrace fixtures. Got {embracers}")

    if len(embracers) == 0:
        return

    (sut,) = embracers
    cls = registry[sut]
    table = getattr(metafunc.module, "table", None)
    if table is not None:
        cases = table
    else:
        cases = [from_module(cls, metafunc.module)]

    metafunc.parametrize("case", cases, ids=[str(c) for c in cases])
