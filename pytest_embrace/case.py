# skip the future import because it breaks dataclass.fields()
# and turns each Field.type to a string!
# isort: dont-add-import: from __future__ import annotations

import re
import sys
from dataclasses import _MISSING_TYPE, MISSING, Field, dataclass, field, fields
from types import MappingProxyType
from typing import Any, Callable, Dict, Generic, Mapping, Optional, Type, TypeVar, Union

from pytest_embrace.anno import AnnotationInfo, get_pep_593_values
from pytest_embrace.exc import CaseConfigurationError

CaseType = TypeVar("CaseType")
CoCaseType = TypeVar("CoCaseType", contravariant=True)


@dataclass
class CaseArtifact(Generic[CoCaseType]):
    """Wrap the result of test executions.
    Contains the CaseType object created from the enclosing module.
    Conrains the result returned (or yielded) from the case fixture."""

    case: CoCaseType
    actual_result: Any = None


CaseArtifactType = TypeVar("CaseArtifactType", bound=CaseArtifact, covariant=True)
CaseRunner = Callable[..., Any]


CaseCls = TypeVar("CaseCls")
TUnset = object
UNSET: TUnset = object()


@dataclass
class AttrInfo:
    dc_field: Field
    annotations: Optional[AnnotationInfo] = None
    name: str = field(init=False)

    def __post_init__(self) -> None:
        self.name = self.dc_field.name


@dataclass
class CaseTypeInfo(Generic[CaseCls]):
    type: Type[CaseCls]
    fixture_name: Union[str, TUnset] = UNSET
    type_name: str = field(init=False)
    type_attrs: Dict[str, AttrInfo] = field(default_factory=dict)
    generators: Dict[str, Callable[..., CaseCls]] = field(default_factory=dict)
    skip_validation: bool = False

    def __post_init__(self) -> None:
        self.type_name = self.type.__name__
        self.type_annotations = get_pep_593_values(self.type)
        self.type_attrs = {
            f.name: AttrInfo(dc_field=f, annotations=self.type_annotations.get(f.name))
            for f in fields(self.type)
        }


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


def _kw_only_maybe(kw_only: bool) -> Dict[str, bool]:
    return {} if sys.version_info < (3, 10) else {"kw_only": kw_only}


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

    field_ = __field(
        default=default_,
        init=init,
        default_factory=default_factory,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata={**metadata, "trickle": Trickle(no_override)},
        **_kw_only_maybe(kw_only),
    )
    return field_


def _pass_thru_parser(extracted: str) -> Any:
    return extracted


def derive_from_filename(
    *,
    pattern: str = r"[\w\.]*test_([\w].*)",
    parse: Callable[[str], Any] = _pass_thru_parser,
    # context: Dict[Any, Any] = None,
    default: Any = MISSING,
    default_factory: Union[Callable[[], Any], OptionalMissing] = MISSING,
    init: bool = True,
    repr: bool = True,
    hash: Optional[bool] = None,
    compare: bool = True,
    metadata: Optional[Mapping[Any, Any]] = None,
    kw_only: bool = False,
) -> Any:
    """Marks an attribute as derived from the name of an enclosing test file."""
    if metadata is None:
        metadata = MappingProxyType({})

    if default is MISSING and default_factory is MISSING:
        default_ = DeriveFromFileName(pattern, parse=parse)
    else:
        default_ = default

    field_: Field = trickles(
        default=default_,
        init=init,
        default_factory=default_factory,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata={
            **metadata,
            "trickle": Trickle(no_override=True),
            "derive_from_filename": default_,
        },
        **_kw_only_maybe(kw_only),
    )
    return field_


class DeriveFromFileName:
    """Extract the value of the annotated attribute from the test's filename
    based on the given regex."""

    def __init__(
        self,
        file_pattern: str = r"[\w\.]*test_([\w].*)",
        *,
        parse: Callable[[str], Any] = _pass_thru_parser,
    ):
        self.file_pattern: re.Pattern = re.compile(file_pattern)
        self.parse = parse

    def get_attr_value(self, filename: str) -> Any:
        match = self.file_pattern.search(filename)
        if match is None:
            raise CaseConfigurationError(
                f"Could not derive a value from filename {filename}"
                f" with regex {self.file_pattern}. :("
            )
        extracted = match.group(1)

        return self.parse(extracted)
