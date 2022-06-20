from typing import Any, Generic, Protocol, TypeVar

CaseType = TypeVar("CaseType")
CoCaseType = TypeVar("CoCaseType", contravariant=True)


class CaseArtifact(Generic[CoCaseType]):
    case: CoCaseType
    actual_result: Any


CaseArtifactType = TypeVar("CaseArtifactType", bound=CaseArtifact, covariant=True)


class CaseRunner(Protocol[CoCaseType, CaseArtifactType]):
    def __call__(self, case: CoCaseType) -> CaseArtifactType:
        ...

    __name__: str
