from dataclasses import Field, fields
from inspect import getmodule
from textwrap import dedent
from typing import Type

from pytest_embrace.anno import AnnotationMap, get_pep_593_values

from .embrace import registry
from .exc import EmbraceError


class EmbraceTestGenError(EmbraceError):
    ...


def _stringify_type(type: Type) -> str:
    return str(type) if not repr(type).startswith("<class") else type.__name__


def _field_to_cute_type_hint(field: Field, anno_map: AnnotationMap) -> str:
    type_hint = _stringify_type(field.type)
    if field.name not in anno_map:
        return f"{field.name}: {type_hint}"

    anno_info = anno_map[field.name]
    comment = next((v for v in anno_info.annotations if isinstance(v, str)), None)
    type_hint = _stringify_type(anno_info.type)
    text = f"{field.name}: {type_hint}"
    if comment is not None:
        text += f"  # {comment}"
    return text


def gen_text(name: str, table: bool = False) -> str:
    case_type = registry().get(name)
    if case_type is None:
        raise EmbraceTestGenError(f"No such test type '{name}'.")

    anno_map = get_pep_593_values(case_type)

    type_hints = "\n".join(
        _field_to_cute_type_hint(f, anno_map) for f in fields(case_type)
    )

    source = getmodule(case_type)
    case_import = (
        dedent(
            f"""
            from {mod_name} import {case_type.__name__}
            """
        )
        if (mod_name := getattr(source, "__name__", None)) is not None
        else ""
    )

    # not using dedent bc newlines in the type hints are hard
    return f"""
from pytest_embrace import CaseArtifact
{case_import}

{type_hints}


def test({name}: CaseArtifact[{case_type.__name__}]) -> None:
    ...
            """
