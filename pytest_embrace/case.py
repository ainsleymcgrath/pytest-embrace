import re
import sys
from collections import defaultdict
from dataclasses import _MISSING_TYPE, MISSING, Field, dataclass, field, fields
from inspect import getmodule
from operator import itemgetter
from textwrap import dedent
from types import MappingProxyType
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Mapping,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

import isort
from black import format_str
from black.mode import Mode

from pytest_embrace.anno import AnnotationInfo, get_pep_593_values
from pytest_embrace.exc import CaseConfigurationError
from pytest_embrace.undot import undot_type_str

CaseType = TypeVar("CaseType")
CoCaseType = TypeVar("CoCaseType", contravariant=True)


@dataclass
class CaseArtifact(Generic[CoCaseType]):
    case: CoCaseType
    actual_result: Any = None


CaseArtifactType = TypeVar("CaseArtifactType", bound=CaseArtifact, covariant=True)
CaseRunner = Callable[..., Any]


CaseCls = TypeVar("CaseCls", bound=Type)
TUnset = object
UNSET: TUnset = object()


def _stringify_type(type: Type) -> str:
    return str(type) if not repr(type).startswith("<class") else type.__name__


def _unnest_generics(type: Union[Type, List[Type]]) -> Iterator[Type]:
    if isinstance(type, list):  # such as the first arg to Callable[]
        for member in type:
            yield from _unnest_generics(member)
        return

    generic_args = get_args(type)
    if generic_args == tuple():
        yield type
    elif (origin := get_origin(type)) is not None:
        yield origin

    for arg in generic_args:
        yield from _unnest_generics(arg)


@dataclass
class AttrInfo:
    dc_field: Field
    annotations: Optional[AnnotationInfo] = None
    name: str = field(init=False)

    def __post_init__(self) -> None:
        self.name = self.dc_field.name

    def as_hint(self) -> str:
        typ = self.dc_field.type if self.annotations is None else self.annotations.type
        type_str = undot_type_str(_stringify_type(typ))
        # get rid of dots since CaseTypeInfo solves the imports
        type_str_parts = [t.lstrip("[").rstrip("]") for t in type_str.split(".")]
        if len(type_str_parts) > 1:
            type_str = type_str_parts[-1]
        comment = next(
            (
                v
                for v in getattr(self.annotations, "annotations", [])
                if isinstance(v, str)
            ),
            None,
        )
        text = f"{self.name}: {type_str}"
        if comment is not None:
            text += f"  # {comment}"
        return text

    def render_import_statement(self) -> str:
        lookup: Dict[str, List[str]] = defaultdict(list)
        for typ in _unnest_generics(self.dc_field.type):
            modname = getattr(typ, "__module__", "")
            if modname == "builtins" or modname == "":
                continue
            if sys.version_info < (3, 9) and "collections.abc" in modname:
                # from 3.9 and onwards, things like Mapping and Callable
                # are aliases of collections.abc types.
                # before then, the stuff from collections.abc was not subscriptable,
                # so here we are.
                modname = "typing"
            own_name: str = getattr(
                typ,
                "__name__",
                getattr(
                    typ,
                    # as in the case of typing.Union in <=3.9,
                    # whose __class__ is a _SpecialForm
                    "_name",
                    getattr(
                        typ.__class__,
                        "__name__",
                    ),
                ),
            )
            if own_name == "Annotated":
                continue
            lookup[modname].append(own_name)

        return "\n".join(
            f"from {modname} import {', '.join(sorted(target))}"
            for modname, target in sorted(lookup.items(), key=itemgetter(0))
        )


@dataclass
class CaseTypeInfo(Generic[CaseCls]):
    type: CaseCls
    caller_name: Union[str, TUnset] = UNSET
    type_name: str = field(init=False)
    type_attrs: Dict[str, AttrInfo] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.type_name = self.type.__name__
        self.type_annotations = get_pep_593_values(self.type)
        self.type_attrs = {
            f.name: AttrInfo(dc_field=f, annotations=self.type_annotations.get(f.name))
            for f in fields(self.type)
        }

    def to_text(self) -> str:
        type_hints = "\n".join(attr.as_hint() for attr in self.type_attrs.values())

        source = getmodule(self.type)
        case_import = (
            dedent(
                f"""
                from {mod_name} import {self.type_name}

                """
            )
            if (mod_name := getattr(source, "__name__", None)) is not None
            else ""
        )

        imports = "\n".join(
            attr_info.render_import_statement()
            for attr_info in self.type_attrs.values()
        )

        # not using dedent bc newlines in the type hints are hard
        return format_str(
            isort.code(
                f"""
from pytest_embrace import CaseArtifact
{imports}
{case_import}
{type_hints}


def test({self.caller_name}: CaseArtifact[{self.type_name}]) -> None:
    ...""",
                profile="black",
            ),
            mode=Mode(),
        )


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
