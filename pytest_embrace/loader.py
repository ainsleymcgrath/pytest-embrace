from dataclasses import fields, is_dataclass
from types import ModuleType
from typing import Type

from .case import CaseType
from .exc import CaseConfigurationError


def from_module(cls: Type[CaseType], module: ModuleType) -> CaseType:
    if not is_dataclass(cls):
        raise CaseConfigurationError("Must use a dataclass for case object.")

    kwargs = {
        f.name: getattr(module, f.name) for f in fields(cls) if f.name in dir(module)
    }
    return cls(**kwargs)
