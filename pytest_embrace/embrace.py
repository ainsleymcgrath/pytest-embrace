from __future__ import annotations

from collections.abc import Iterator
from functools import partial
from inspect import signature
from typing import Callable, Dict, Generic
from typing import MutableMapping as TMutableMapping
from typing import Type, TypeVar

import pytest

from .case import CaseArtifact, CaseRunner, CaseType, CaseTypeInfo
from .exc import CaseConfigurationError

RegistryValue = Type["CaseType"]

T = TypeVar("T", bound=Type)
TUnset = object
UNSET: TUnset = object()


TCaseInfo = TypeVar("TCaseInfo", bound=CaseTypeInfo)


class CaseTypeRegistry(TMutableMapping[str, TCaseInfo]):
    def __init__(self) -> None:
        self._mapping: Dict[str, TCaseInfo] = {}

    def __getitem__(self, key: str) -> TCaseInfo:
        return self._mapping[key]

    def __setitem__(self, key: str, val: TCaseInfo) -> None:
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

    def __str__(self) -> str:
        return "\n".join(f"{name}  (via {cls})" for name, cls in self.items())


_registry: CaseTypeRegistry[CaseTypeInfo] = CaseTypeRegistry()


class Embrace(Generic[CaseType]):
    # _runner_registry: ClassVar[OneTimeOnlyMapping] = OneTimeOnlyMapping()

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
    ) -> Callable[[pytest.FixtureRequest, CaseType], Iterator[CaseArtifact]]:
        _registry[name] = CaseTypeInfo(type=self.case_type, caller_name=name)
        self.caller_fixture_name = name

        @pytest.fixture
        def caller_fixture(
            request: pytest.FixtureRequest, case: CaseType
        ) -> Iterator[CaseArtifact[CaseType]]:
            assert self.wrapped_func is not None
            # calling `getfixturevalue` for the wrapped func gets `run_case_fixture`.
            # doing *that* assigns self.runner at the last possible moment
            request.getfixturevalue(self.wrapped_func.__name__)
            assert self.runner is not None
            # bring the artifact into scope with the case attached
            # so debug/exception output can see it in locals()
            artifact = CaseArtifact(case=case)
            run_result = self.runner(case)
            try:
                # fixtures with cleanup yield once
                test_result = next(run_result)
            except TypeError:
                test_result = run_result

            artifact.actual_result = test_result
            yield artifact

            try:
                # trigger the cleanup of the runner, if needed
                next(run_result, ...)
            except TypeError:
                pass

        return caller_fixture


def registry() -> CaseTypeRegistry[CaseTypeInfo]:
    return _registry
