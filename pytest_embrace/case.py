import sys
from dataclasses import _MISSING_TYPE, MISSING, Field, dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Generic, Mapping, Optional, Protocol, TypeVar, Union

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


OptionalMissing = Optional[_MISSING_TYPE]


def __field(**kwargs: Any) -> Field:
    """Fighting with overload variants of `field()` was so hard.
    This feels like an ok hack for now."""
    return field(**kwargs)


def trickles(
    *,
    no_override: bool = False,
    default: Any = MISSING,
    default_factory: Union[Callable[[], Any], OptionalMissing] = MISSING,
    init: bool = True,
    repr: bool = True,
    hash: Optional[bool] = None,
    compare: bool = True,
    metadata: Optional[Mapping[Any, Any]] = None,
    kw_only: bool = False,
) -> Any:
    """Marks an attribute as one that can 'trickle down' from module scope
    into table cases as a default value.

    Attempts to remain faithful to the field() API."""
    if metadata is None:
        metadata = MappingProxyType({})

    if default is MISSING and default_factory is MISSING:
        default_ = Trickle(no_override)
    else:
        default_ = default

    kw_only_maybe = {} if sys.version_info < (3, 10) else {"kw_only": kw_only}

    field_ = __field(
        default=default_,
        init=init,
        default_factory=default_factory,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata={**metadata, "trickle": Trickle(no_override)},
        **kw_only_maybe,
    )
    return field_
