from collections.abc import MutableMapping
from dataclasses import fields, is_dataclass
from types import ModuleType
from typing import Any, Generic, Iterator, Protocol, Type, TypeVar

from .exc import EmbraceError


class CaseConfigurationError(EmbraceError):
    ...


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


CaseType = TypeVar("CaseType")
CoCaseType = TypeVar("CoCaseType", contravariant=True)


def from_module(cls: Type[CaseType], module: ModuleType) -> CaseType:
    if not is_dataclass(cls):
        raise CaseConfigurationError("Must use a dataclass for case object.")

    kwargs = {
        f.name: getattr(module, f.name) for f in fields(cls) if f.name in dir(module)
    }
    return cls(**kwargs)


class CaseArtifact(Generic[CoCaseType]):
    case: CoCaseType
    actual_result: Any


CaseArtifactType = TypeVar("CaseArtifactType", bound=CaseArtifact, covariant=True)


class CaseRunner(Protocol[CoCaseType, CaseArtifactType]):
    def __call__(self, case: CoCaseType) -> CaseArtifactType:
        ...

    __name__: str
