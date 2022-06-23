from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar

CaseType = TypeVar("CaseType")
CoCaseType = TypeVar("CoCaseType", contravariant=True)


@dataclass
class CaseArtifact(Generic[CoCaseType]):
    case: CoCaseType
    actual_result: Any


CaseArtifactType = TypeVar("CaseArtifactType", bound=CaseArtifact, covariant=True)


class CaseRunner(Protocol[CoCaseType, CaseArtifactType]):
    def __call__(self, case: CoCaseType) -> CaseArtifactType:
        ...


class Trickle:
    """This type is used to identify attributes marked with trickles()."""


def trickles() -> Any:
    """Marks an attribute as one that can 'trickle down' from module scope
    into table cases as a default value."""
    return Trickle()
