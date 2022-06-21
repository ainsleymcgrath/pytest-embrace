from __future__ import annotations

from collections.abc import Iterator, MutableMapping
from functools import partial
from inspect import signature
from typing import Callable, ClassVar, Generic, Type

import pytest

from .case import CaseRunner, CaseType
from .exc import CaseConfigurationError

RegistryValue = Type["CaseType"]


class OneTimeOnlyMapping(MutableMapping):
    def __init__(self) -> None:
        self._mapping: dict[str, RegistryValue] = {}

    def __getitem__(self, key: str) -> RegistryValue:
        return self._mapping[key]

    def __setitem__(self, key: str, val: RegistryValue) -> None:
        if key not in self._mapping:
            self._mapping[key] = val
            return

        existing = self._mapping[key]

        if type(existing) == type(val):
            return

        raise CaseConfigurationError(
            f"Already registered a case fixture called for {key} for {val}."
        )

    def __iter__(self) -> Iterator[str]:
        return iter(self._mapping)

    def __len__(self) -> int:
        return len(self._mapping)

    def __delitem__(self, _: str) -> None:
        raise NotImplementedError


class Embrace(Generic[CaseType]):
    _runner_registry: ClassVar[OneTimeOnlyMapping] = OneTimeOnlyMapping()

    def __init__(self, case_type: Type[CaseType]):
        self.case_type = case_type
        self.wrapped_func: CaseRunner | None = None
        self.runner: partial | None = None

    def register_case_runner(
        self, func: CaseRunner
    ) -> Callable[[pytest.FixtureRequest], partial]:

        self.wrapped_func = func

        @pytest.fixture
        def run_case_fixture(request: pytest.FixtureRequest) -> partial:
            sig = signature(func)
            kwargs = {
                name: request.getfixturevalue(name)
                for name, param in sig.parameters.items()
                if param.annotation != self.case_type
            }
            self.runner = partial(func, **kwargs)

            return self.runner

        return run_case_fixture

    def caller_fixture_factory(
        self, name: str
    ) -> Callable[[pytest.FixtureRequest, CaseType], None]:
        self.__class__._runner_registry[name] = self.case_type
        self.caller_fixture_name = name

        @pytest.fixture
        def caller_fixture(request: pytest.FixtureRequest, case: CaseType) -> None:
            assert self.wrapped_func is not None
            # calling `getfixturevalue` for the wrapped func gets `run_case_fixture`.
            # doing *that* assigns self.runner at the last possible moment
            request.getfixturevalue(self.wrapped_func.__name__)  # type: ignore
            assert self.runner is not None
            self.runner(case)

        return caller_fixture
