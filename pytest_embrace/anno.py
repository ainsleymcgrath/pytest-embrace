from dataclasses import dataclass
from re import Pattern, compile
from typing import Any, Callable, Dict, List, Type, get_args


@dataclass
class Comment:
    text: str


class Prompt:
    """When tests are generated via `--embrace`, prompt the user for this value."""


def _pass_thru_parser(extracted: str, context: Dict[Any, Any]) -> Any:
    return extracted


class DeriveNameFromFile:
    """Extract the value of the annotated attribute from the test's filename
    based on the given regex."""

    def __init__(
        self,
        file_pattern: str = r"test_(\w.*)",
        *,
        parse: Callable[[str, Dict[Any, Any]], Any] = _pass_thru_parser,
        context: Dict[Any, Any] = None
    ):
        self.file_pattern: Pattern = compile(file_pattern)
        self.parse = parse
        self.context = context or {}

    def get_attr_value(self, filename: str) -> Any:
        match = self.file_pattern.search(filename)
        if match is None:
            raise
        extracted = match.group(1)

        return self.parse(extracted, self.context)


@dataclass
class AnnotationInfo:
    type: Any
    annotations: List[Any]


AnnotationMap = Dict[str, AnnotationInfo]


def get_pep_593_values(cls: Type) -> AnnotationMap:
    out: AnnotationMap = {}
    for k, v in cls.__annotations__.items():
        attr_name = getattr(v, "__name__", getattr(v.__class__, "__name__", ""))
        if attr_name not in {"Annotated", "_AnnotatedAlias"}:
            continue
        typ, *annotations = get_args(v)
        out[k] = AnnotationInfo(typ, annotations)
    return out
