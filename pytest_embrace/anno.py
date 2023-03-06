from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Type, get_args

# class Prompt:
#     """When tests are generated via `--embrace`, prompt the user for this value."""


@dataclass
class AnnotationInfo:
    type: Any
    annotations: List[Any]


AnnotationMap = Dict[str, AnnotationInfo]


def get_pep_593_values(cls: Type) -> AnnotationMap:
    """Map string names of attributes to their annotation metadata."""
    out: AnnotationMap = {}
    for k, v in cls.__annotations__.items():
        attr_name = getattr(v, "__name__", getattr(v.__class__, "__name__", ""))
        if attr_name not in {"Annotated", "_AnnotatedAlias"}:
            continue
        typ, *annotations = get_args(v)
        out[k] = AnnotationInfo(typ, annotations)
    return out
