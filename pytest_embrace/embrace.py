from __future__ import annotations

from collections.abc import Iterator
from functools import partial
from inspect import signature
from typing import Any, Callable, Generic
from typing import MutableMapping as TMutableMapping
from typing import Type, TypeVar

import pytest
from typing_extensions import ParamSpec

from .case import CaseArtifact, CaseRunner, CaseType, CaseTypeInfo
from .exc import CaseConfigurationError

RegistryValue = Type["CaseType"]

T = TypeVar("T", bound=Type)
TUnset = object
UNSET: TUnset = object()
CodeGenFuncArgs = ParamSpec("CodeGenFuncArgs")
CodeGenFuncReturn = TypeVar("CodeGenFuncReturn")


TCaseInfo = TypeVar("TCaseInfo", bound=CaseTypeInfo)


class CaseTypeRegistry(TMutableMapping[str, TCaseInfo]):
    def __getitem__(self, key: str) -> TCaseInfo:
        return self.__dict__[key]

    def __setitem__(self, key: str, val: TCaseInfo) -> None:
        if key not in self.__dict__:
            self.__dict__[key] = val
            return

        existing = self.__dict__[key]

        if type(existing) == type(val):
            return

        raise CaseConfigurationError(
            f"Already registered a case fixture called for {key} for {val}."
        )

    def __iter__(self) -> Iterator[str]:
        return iter(self.__dict__)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __delitem__(self, _: str) -> None:
        raise NotImplementedError

    def __str__(self) -> str:
        return "\n".join(f"{name}  (via {cls})" for name, cls in self.items())


_registry: CaseTypeRegistry[CaseTypeInfo] = CaseTypeRegistry()


class Embrace(Generic[CaseType]):
    """The entrypoint for creating test cases from a dataclass.
    Register a dataclass as a module test schema and create a configurator for defining
    how tests that implement it will run."""

    def __init__(self, case_type: Type[CaseType], skip_validation: bool = False):
        self.case_type = case_type
        self.wrapped_func: CaseRunner | None = None
        self.runner: partial | None = None
        self.generators: dict[str, Callable[..., Any]]
        self.fixture_name: str = ""
        self.skip_validation = skip_validation

    def fixture(
        self, func: CaseRunner
    ) -> Callable[[CaseType, pytest.FixtureRequest], Iterator[CaseArtifact[CaseType]]]:
        """Create a fixture to use in Embrace module-based tests.

        The decorated function is a 'virtual' fixture, insofar as its ultimately just
        a plain function. The generated fixture gets parametrized
        (during pytest_generate_tests) with CaseType objects built from enclosing test
        modules and then later calls that decorated function with fixture values."""
        self.fixture_name = func.__name__
        _registry[self.fixture_name] = CaseTypeInfo(
            type=self.case_type,
            fixture_name=func.__name__,
            skip_validation=self.skip_validation,
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

    def generator(
        self, func: Callable[CodeGenFuncArgs, CodeGenFuncReturn]
    ) -> Callable[CodeGenFuncArgs, CodeGenFuncReturn]:
        _registry[self.fixture_name].generators[func.__name__] = func

        def render(
            *args: CodeGenFuncArgs.args, **kwargs: CodeGenFuncArgs.kwargs
        ) -> CodeGenFuncReturn:
            case_or_case_iter = func(*args, **kwargs)
            if isinstance(case_or_case_iter, Iterator):
                module_vars = next(case_or_case_iter)
                return module_vars  # TODO!
            else:
                # assert isinstance(case_or_case_iter, CaseType)
                return case_or_case_iter

        return render


def registry() -> CaseTypeRegistry[CaseTypeInfo]:
    return _registry
