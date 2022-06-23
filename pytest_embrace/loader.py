from __future__ import annotations

from dataclasses import Field, asdict, dataclass, field, fields, is_dataclass
from types import ModuleType
from typing import Any, Dict, List, Type, Union

from pydantic import create_model
from pydantic.error_wrappers import ValidationError
from pydantic.types import StrictBool, StrictBytes, StrictFloat, StrictInt, StrictStr

# from . import anno
from .case import CaseType, Trickle
from .exc import CaseConfigurationError


class Sentinel:
    ...


@dataclass
class AttrInfo:
    dc_field: Field
    module_value: Any
    name: str = field(init=False)

    def __post_init__(self) -> None:
        self.name = self.dc_field.name


ShouldBecomeStrictBuiltinTypes = Union[str, bytes, int, float, bool]
StrictPydanticTypes = Union[StrictStr, StrictBytes, StrictInt, StrictFloat, StrictBool]

PYDANTIC_STRICTIFICATION_MAP = {
    str: StrictStr,
    bytes: StrictBytes,
    int: StrictInt,
    float: StrictFloat,
    bool: StrictBool,
}


def _strictify(
    t: Any,
) -> Union[Type[StrictPydanticTypes], Type[ShouldBecomeStrictBuiltinTypes], Type[Any]]:
    return PYDANTIC_STRICTIFICATION_MAP.get(t, t)


class ModuleInfo:
    def __init__(self, *, cls: Type[CaseType], mod: ModuleType):
        defined = dir(mod)
        spec = fields(cls)
        validator_kwargs: Dict[str, Any] = {}
        self.attrs: Dict[str, AttrInfo] = {}

        for field_ in spec:
            if field_.name not in defined:
                continue

            if field_.name == "table":
                raise CaseConfigurationError(
                    "You've chosen the only illegal property name!"
                    " It's used by the framwork. Please say 'table_' instead."
                )

            if field_.name == "should":
                # 'should' gets special treatment
                pass

            module_value = getattr(mod, field_.name)
            attr_info = AttrInfo(field_, module_value)
            self.attrs[attr_info.name] = attr_info

            validator_kwargs[field_.name] = (
                _strictify(attr_info.dc_field.type),
                module_value,
            )

        Validator = create_model(f"{mod.__name__}__ModuleValidator", **validator_kwargs)
        Validator(**self.kwargs())

    def kwargs(self) -> Dict[str, Any]:
        return {a.name: a.module_value for a in self.attrs.values()}


def _raise_non_dataclass(o: object) -> None:
    if not is_dataclass(o):
        raise CaseConfigurationError("Must use a dataclass for case object.")


def _report_validation_error(exc: ValidationError, *, target_name: str) -> None:
    errors = exc.errors()
    errors_disambiguation = "\n".join(
        f"    Variable/Arg '{e['loc'][0]}'"
        f" should be of type {e['type'].lstrip('type_error.')}"
        for e in errors
    )
    raise CaseConfigurationError(
        f"{len(errors)} invalid attr values in '{target_name}':\n"
        f"{errors_disambiguation}"
    ) from exc


def from_module(cls: Type[CaseType], module: ModuleType) -> CaseType:
    _raise_non_dataclass(cls)

    try:
        info = ModuleInfo(mod=module, cls=cls)
    except ValidationError as e:
        _report_validation_error(e, target_name=module.__name__)

    try:
        return cls(**info.kwargs())
    except TypeError:
        raise CaseConfigurationError(
            f"Incorrect or missing attributes in module {module.__name__}."
            f"\nGot attributes {set(info.kwargs())}"
        )


class PydanticConfig:
    arbitrary_types_allowed = True


def revalidate_dataclass(case: CaseType, *, alias: str) -> CaseType:
    _raise_non_dataclass(case)
    kwargs = asdict(case)
    validator_kwargs: Dict[str, Any] = {
        k: (_strictify(type(v)), v) for k, v in kwargs.items()
    }

    Validator = create_model(
        f"{case.__class__.__name__}__CaseValidator",
        **validator_kwargs,
        __config__=PydanticConfig,  # type: ignore
    )

    try:
        Validator(**kwargs)
    except ValidationError as e:
        _report_validation_error(e, target_name=alias)

    return case


def handle_table_trickle_down(
    cls: Type[CaseType], module: ModuleType
) -> List[CaseType]:
    table = getattr(module, "table", None)
    assert table is not None

    trickle_attr_defaults = {
        attr: getattr(module, attr)
        for attr in dir(cls)
        if not attr.startswith("__") and isinstance(getattr(cls, attr), Trickle)
    }
    # annotated_module_attrs = {k: pep593[k] for k in dir(module) if k in pep593}

    out: List[CaseType] = []
    for i, case_ in enumerate(table):
        case = revalidate_dataclass(case_, alias=f"{cls.__name__} #{i + 1}")
        for k, v in asdict(case).items():
            if isinstance(v, Trickle):
                setattr(case, k, trickle_attr_defaults[k])

        out.append(case)

    return out
