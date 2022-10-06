from __future__ import annotations

from collections.abc import Iterator
from functools import partial
from inspect import signature
from typing import Any, Callable, Dict, Generic
from typing import MutableMapping as TMutableMapping
from typing import NoReturn, Type, TypeVar

import pytest

from .case import CaseArtifact, CaseRunner, CaseType, CaseTypeInfo
from .exc import CaseConfigurationError, TwoStepApiDeprecationError

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
    """The entrypoint for creating test cases from a dataclass.
    Register a dataclass as a module test schema and create a configurator for defining
    how tests that implement it will run."""

    def __init__(self, case_type: Type[CaseType]):
        self.case_type = case_type
        self.wrapped_func: CaseRunner | None = None
        self.runner: partial | None = None

    def register_case_runner(self, *_: Any) -> NoReturn:
        raise TwoStepApiDeprecationError(deprecated_method="register_case_runner")

    def caller_fixture_factory(self, *_: Any) -> NoReturn:
        raise TwoStepApiDeprecationError(deprecated_method="caller_fixture_factory")

    def fixture(
        self, func: CaseRunner
    ) -> Callable[[CaseType, pytest.FixtureRequest], Iterator[CaseArtifact[CaseType]]]:
        """Create a fixture to use in Embrace module-based tests.

        The decorated function is a 'virtual' fixture, insofar as its ultimately just
        a plain function. The generated fixture gets parametrized
        (during pytest_generate_tests) with CaseType objects built from enclosing test
        modules and then later calls that decorated function with fixture values."""
        _registry[func.__name__] = CaseTypeInfo(
            type=self.case_type,
            caller_name=func.__name__,
        )

        @pytest.fixture
        def fix(
            case: CaseType,
            request: pytest.FixtureRequest,
        ) -> Iterator[CaseArtifact[CaseType]]:
            """The _real_ fixture that calls the decorated 'virtual' one.

            Uses the FixtureRequest to find values for fixtures based on the virtual
            fixture's parameter names."""
            sig = signature(func)
            kwargs = {name: request.getfixturevalue(name) for name in sig.parameters}
            artifact = CaseArtifact(case=case)
            run_result = func(**kwargs)
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

        return fix


def registry() -> CaseTypeRegistry[CaseTypeInfo]:
    return _registry
