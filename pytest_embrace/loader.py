from __future__ import annotations

from dataclasses import MISSING, Field, asdict, dataclass, field, fields, is_dataclass
from types import ModuleType
from typing import Any, Dict, Generic, List, Tuple, Type, Union

from pydantic import create_model
from pydantic.error_wrappers import ValidationError
from pydantic.types import StrictBool, StrictBytes, StrictFloat, StrictInt, StrictStr

from .anno import get_pep_593_values
from .case import CaseType, Trickle
from .exc import CaseConfigurationError


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
    # in dataclasses, Field.type is a string at times
    "str": StrictStr,
    "bytes": StrictBytes,
    "int": StrictInt,
    "float": StrictFloat,
    "bool": StrictBool,
}


# TODO should take a moduleinfo instead of instantiating
def load(cls: Type[CaseType], module: ModuleType) -> List[CaseType]:
    module_info = ModuleInfo(case_type=cls, module=module)
    if module_info.table is not None:
        module_info.trickle_down_table()
        return [
            revalidate_dataclass(case, alias=f"{module_info}.table[{i}]{case}")
            for i, case in enumerate(module_info.table)
        ]

    return [revalidate_dataclass(module_info.to_case(), alias=str(module_info))]


class ModuleInfo(Generic[CaseType]):
    def __init__(self, *, case_type: Type[CaseType], module: ModuleType):
        self.case_type = case_type
        self.module = module
        self.name = module.__name__
        self.cls_fields = {field.name: field for field in fields(self.case_type)}
        self.filename_values = {
            k: derive.get_attr_value(module.__name__)
            for k, v in self.cls_fields.items()
            if (derive := v.metadata.get("derive_from_filename")) is not None
        }
        self.module_attrs = {
            attr: getattr(module, attr)
            for attr in dir(module)
            if not attr.startswith("__") and attr in self.cls_fields
        }
        self.module_attrs.update(self.filename_values)

        if "table" in dir(module):
            self.table = getattr(module, "table")
            is_valid_table = (
                isinstance(self.table, list)
                and len(self.table) > 0
                # would love to use an isinstance() here, but somehow
                # (in Pytester tests specifically)
                # it managed to not work? despite extensive time in PDB?
                and all(str(type(x)) == str(self.case_type) for x in self.table)
            )
            if not is_valid_table:
                raise
        else:
            self.table = None

        self.pep_539 = get_pep_593_values(self.case_type)
        UNSET = object()
        self.trickle_defaults: Dict[str, Tuple[Any, Trickle]] = {
            k: (self.module_attrs.get(k, UNSET), trickle)
            for k, v in self.cls_fields.items()
            if (trickle := v.metadata.get("trickle")) is not None
        }
        self.all_trickles_unset = len(self.trickle_defaults) and all(
            v is UNSET for v, _ in self.trickle_defaults.values()
        )

    def __str__(self) -> str:
        return f"Module[{self.name}]"

    def to_case(self) -> CaseType:
        kwargs = {k: v for k, v in self.module_attrs.items() if k != "table"}
        try:
            return self.case_type(**kwargs)
        except TypeError:
            raise CaseConfigurationError(
                f"Incorrect or missing attributes in {self.name}."
                f"\nOnly got attributes {kwargs}"
            )

    def trickle_down_table(self) -> None:
        assert self.table is not None
        for i, case in enumerate(self.table):
            for k, v in asdict(case).items():
                if k in self.filename_values:
                    setattr(case, k, self.filename_values[k])
                elif self.all_trickles_unset and isinstance(v, Trickle):
                    raise CaseConfigurationError(
                        f"'{k}' is unset at the module level and in table[{i}]:{case}."
                        " '{k}' is marked as 'trickles()' so it must be set somewhere."
                    )
                elif k in self.trickle_defaults and isinstance(v, Trickle):
                    # absorb the default trickle value
                    (trickle_value, _) = self.trickle_defaults[k]
                    setattr(case, k, trickle_value)
                elif k in self.trickle_defaults:
                    # there was a trickle, but it was overridden
                    (_, trickle_config) = self.trickle_defaults[k]
                    if trickle_config.no_override and k in self.module_attrs:
                        raise CaseConfigurationError(
                            f"Trickle-down attribute '{k}"
                            f" cannot be overridden in table[{i}]:{case}'"
                        )


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


class PydanticConfig:
    arbitrary_types_allowed = True


def revalidate_dataclass(case: CaseType, *, alias: str) -> CaseType:
    _raise_non_dataclass(case)
    kwargs = asdict(case)
    pep539 = get_pep_593_values(type(case))
    validator_kwargs: Dict[str, Tuple[Any, Any]] = {
        field.name: (
            PYDANTIC_STRICTIFICATION_MAP.get(
                pep539[field.name].type if field.name in pep539 else field.type,
                field.type,
            ),
            field.default
            if field.default is not MISSING
            else (
                field.default_factory() if field.default_factory is not MISSING else ...
            ),
        )
        for field in fields(case)
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
