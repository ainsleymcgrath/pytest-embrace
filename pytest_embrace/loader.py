from __future__ import annotations

from dataclasses import MISSING, asdict, fields, is_dataclass
from types import ModuleType
from typing import Any, Dict, Generic, List, Mapping, Optional, Tuple, Union

import pytest
from pydantic import create_model
from pydantic.error_wrappers import ValidationError
from pydantic.types import StrictBool, StrictBytes, StrictFloat, StrictInt, StrictStr

from pytest_embrace.case import CaseTypeInfo

from .anno import get_pep_593_values
from .case import CaseType, Trickle
from .exc import CaseConfigurationError, EmbraceError

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


class ModuleInfo(Generic[CaseType]):
    def __init__(self, *, case_type_info: CaseTypeInfo, module: ModuleType) -> None:
        self.case = case_type_info
        self.module = module
        self.name = module.__name__
        self.cls_fields = {field.name: field for field in fields(self.case.type)}
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

        self.table = getattr(module, "table", None)
        self.has_table_of_tests = (
            isinstance(self.table, list)
            and len(self.table) > 0
            # would love to use an isinstance() here, but somehow
            # (in Pytester tests specifically)
            # it managed to not work? despite extensive time in PDB?
            and all(str(type(x)) == str(self.case.type) for x in self.table)
        )

        self.pep_539 = get_pep_593_values(self.case.type)

        if self.has_table_of_tests:
            self._trickle_down_table()

    def __str__(self) -> str:
        return f"Module[{self.name}]"

    def to_case(self) -> CaseType:
        kwargs = {k: v for k, v in self.module_attrs.items() if k != "table"}
        try:
            return self.case.type(**kwargs)
        except TypeError:
            raise CaseConfigurationError(
                f"Incorrect or missing attributes in {self.name}."
                f"\nOnly got attributes {kwargs}"
            )

    def _trickle_down_table(self) -> None:
        assert self.table is not None
        UNSET = object()
        trickle_defaults: Dict[str, Tuple[Any, Trickle]] = {
            k: (self.module_attrs.get(k, UNSET), trickle)
            for k, v in self.cls_fields.items()
            if (trickle := v.metadata.get("trickle")) is not None
        }
        all_trickles_unset = len(trickle_defaults) and all(
            v is UNSET for v, _ in trickle_defaults.values()
        )

        for i, case in enumerate(self.table):
            for k, v in asdict(case).items():
                if k in self.filename_values:
                    setattr(case, k, self.filename_values[k])
                elif all_trickles_unset and isinstance(v, Trickle):
                    raise CaseConfigurationError(
                        f"'{k}' is unset at the module level and in table[{i}]:{case}."
                        " '{k}' is marked as 'trickles()' so it must be set somewhere."
                    )
                elif k in trickle_defaults and isinstance(v, Trickle):
                    # absorb the default trickle value
                    (trickle_value, _) = trickle_defaults[k]
                    setattr(case, k, trickle_value)
                elif k in trickle_defaults:
                    # there was a trickle, but it was overridden
                    (_, trickle_config) = trickle_defaults[k]
                    if trickle_config.no_override and k in self.module_attrs:
                        raise CaseConfigurationError(
                            f"Trickle-down attribute '{k}"
                            f" cannot be overridden in table[{i}]:{case}'"
                        )


def load(test: ModuleInfo[CaseType]) -> List[CaseType]:
    if test.table is not None:
        return [
            revalidate_dataclass(case, alias=f"{test}.table[{i}]{case}")
            for i, case in enumerate(test.table)
        ]

    return [revalidate_dataclass(test.to_case(), alias=str(test))]


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


def find_embrace_requester(
    *, metafunc: pytest.Metafunc, registry: Mapping[str, CaseTypeInfo]
) -> Optional[ModuleInfo]:
    potentials = [name for name in metafunc.fixturenames if name in registry]

    if len(potentials) > 1:
        raise EmbraceError(f"Can't request multiple Embrace fixtures. Got {potentials}")

    found = next(iter(potentials), None)
    return (
        found
        if found is None
        else ModuleInfo(case_type_info=registry[found], module=metafunc.module)
    )
