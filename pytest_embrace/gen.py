from dataclasses import fields
from inspect import getmodule
from textwrap import dedent

from .embrace import Embrace
from .exc import EmbraceError


class EmbraceTestGenError(EmbraceError):
    ...


def gen_text(name: str, table: bool = False) -> str:
    case_type = Embrace._runner_registry.get(name)
    if case_type is None:
        raise EmbraceTestGenError(f"No such test type '{name}'.")

    type_hints = "\n".join(
        f"{f.name}:"
        f" {typ if not repr((typ := f.type)).startswith('<class') else typ.__name__}"
        for f in fields(case_type)
    )

    source = getmodule(case_type)
    case_import = (
        dedent(
            f"""
            import {case_type.__name__} from {mod_name}
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
