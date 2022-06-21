# from __future__ import annotations

from dataclasses import Field, dataclass, field, fields, is_dataclass
from inspect import isclass
from types import ModuleType
from typing import Any, Type, get_origin

from pydantic import create_model
from pydantic.error_wrappers import ValidationError

from .case import CaseType
from .exc import CaseConfigurationError


class Sentinel:
    ...


@dataclass
class AttrInfo:
    dc_field: Field
    module_value: Any
    mismatch: bool = False
    name: str = field(init=False)

    def __post_init__(self) -> None:
        origin = get_origin(self.dc_field.type)
        shallow_match_generic = isinstance(self.module_value, origin or Sentinel)
        val_is_subclass = isclass(self.dc_field.type) and issubclass(
            self.dc_field.type, type(self.module_value)
        )
        self.mismatch = not val_is_subclass and not shallow_match_generic
        self.name = self.dc_field.name


class ModuleInfo:
    def __init__(self, *, cls: Type[CaseType], mod: ModuleType):
        defined = dir(mod)
        spec = fields(cls)
        self.attrs: dict[str, AttrInfo] = {}
        self.mismatches: dict[str, AttrInfo] = {}
        validator_kwargs: dict[str, Any] = {}

        for field_ in spec:
            if field_.name not in defined:
                continue
            module_value = getattr(mod, field_.name)
            attr_info = AttrInfo(field_, module_value)
            self.attrs[attr_info.name] = attr_info
            if attr_info.mismatch:
                self.mismatches[attr_info.name] = attr_info

            validator_kwargs[field_.name] = (attr_info.dc_field.type, module_value)

        Validator = create_model(f"{mod.__name__}__ModuleValidator", **validator_kwargs)
        Validator(**self.kwargs())

    def kwargs(self) -> dict[str, Any]:
        return {a.name: a.module_value for a in self.attrs.values()}


def from_module(cls: Type[CaseType], module: ModuleType) -> CaseType:
    if not is_dataclass(cls):
        raise CaseConfigurationError("Must use a dataclass for case object.")

    try:
        info = ModuleInfo(mod=module, cls=cls)
    except ValidationError as e:
        errors = e.errors()
        raise CaseConfigurationError(
            f"{len(errors)} invalid attr values in module '{module.__name__}': {errors}"
        ) from e
    try:
        return cls(**info.kwargs())
    except TypeError:
        raise CaseConfigurationError(
            f"Incorrect or missing attributes in module {module.__name__}."
            "\nGot attributes {{*kwargs}}"
        )
