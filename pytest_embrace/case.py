from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar

CaseType = TypeVar("CaseType")
CoCaseType = TypeVar("CoCaseType", contravariant=True)


@dataclass
class CaseArtifact(Generic[CoCaseType]):
    case: CoCaseType
    actual_result: Any = None


CaseArtifactType = TypeVar("CaseArtifactType", bound=CaseArtifact, covariant=True)


class CaseRunner(Protocol[CoCaseType, CaseArtifactType]):
    def __call__(self, case: CoCaseType) -> CaseArtifactType:
        ...


# for some reason, using a dataclass here was problematic.
class Trickle:
    """This type is used to identify attributes marked with trickles()."""

    def __init__(self, no_override: bool = False):
        self.no_override = no_override


def trickles(*, no_override: bool = False) -> Any:
    """Marks an attribute as one that can 'trickle down' from module scope
    into table cases as a default value."""
    return Trickle(no_override)
