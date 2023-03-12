from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import asdict
from inspect import getmodule
from operator import itemgetter
from textwrap import dedent
from typing import Any, Generic, List, Tuple, Type, Union, cast, get_args, get_origin

import isort
from black import format_str
from black.mode import Mode
from pyperclip import sys

from pytest_embrace.case import AttrInfo, CaseType, CaseTypeInfo, Trickle
from pytest_embrace.embrace import CaseTypeRegistry
from pytest_embrace.exc import CodeGenError
from pytest_embrace.undot import undot_type_str


class CodeGenManager:
    fixture_name: str
    generator_name: str | None
    generator_kwargs: dict[str, Any]
    case_type: CaseTypeInfo | None

    def __init__(self, directive: str, *, registry: CaseTypeRegistry[CaseTypeInfo]):
        # identifier goes <fixture_name>[:<generator_name>]
        identifier, *key_value_pairs = directive.split(" ")
        try:
            self.fixture_name, self.generator_name = identifier.split(":", maxsplit=1)
        except ValueError:
            self.fixture_name = identifier
            self.generator_name = None

        self.generator_kwargs: Any = {}  # Any to quell concerns about **kwargs
        for pair in key_value_pairs:
            key, value = pair.split("=", maxsplit=1)
            try:
                self.generator_kwargs[key] = json.loads(value)
            except json.JSONDecodeError as e:
                # a string is expected to fail when it doesn't come in quoted.
                # only fail on other invalid json
                if not isinstance(value, str):
                    raise CodeGenError(
                        f"Generator '{self.generator_name}' supplied with"
                        f"non-serializeable value '{value}' for argument {key}"
                    ) from e

                # strings don't load
                self.generator_kwargs[key] = value

        self.case_type = registry.get(self.fixture_name)

    def render(self) -> str:
        if self.case_type is None:
            raise TypeError("No case found, can't render.")

        renderer = CaseRender(self.case_type)

        if self.generator_name is None:
            return renderer.skeleton()

        try:
            generator = self.case_type.generators[self.generator_name]
        except KeyError as e:
            raise TypeError(f"No custom generator named {self.generator_name}") from e

        src = generator(**self.generator_kwargs)

        if (
            isinstance(src, self.case_type.type)
            or isinstance(src, list)
            or (
                # two-item iterable where [0] is Case and rest is list[Case]
                len(src) == 2
                and isinstance(src[0], self.case_type.type)
                and isinstance(src[1], list)
            )
        ):
            return renderer.with_values(src, hinted=False)
        else:
            raise CodeGenError(
                f"Invalid return type from generator {self.generator_name}: {type(src)}"
            )


class CaseRender(Generic[CaseType]):
    funcdef_pattern = re.compile(r"\n{0,}def\s+(?P<funcname>\w+)\(.+\).*:")

    def __init__(self, src: CaseTypeInfo[CaseType]):
        self.src = src
        self.attr_render = {
            name: AttrRender(info) for name, info in self.src.type_attrs.items()
        }

    def with_values(
        self,
        values: CaseType
        | tuple[CaseType, list[CaseType]]
        | list[CaseType]
        | RenderModuleBodyValue,
        hinted: bool = True,
        no_body: bool = False,
    ) -> str:
        if isinstance(values, list):
            out = self._with_values_from_list(values)
        elif isinstance(values, RenderModuleBodyValue):
            out = self._expert(values)
        elif isinstance(values, tuple):
            # python 3.8 can't deal with list[] or | union in cast() calls
            # (even with future import)
            out = self._with_mixed_values(cast(Tuple[CaseType, List[CaseType]], values))
        else:
            out = self._with_values_from_case(values, hinted=hinted)
        if no_body:
            return out
        return self.module_text(body=out)

    def module_text(self, *, body: str = "") -> str:
        text = (
            f"{self.imports()}\n{body}\n"
            f"def test({self.src.fixture_name}: CaseArtifact[{self.src.type_name}])"
            " -> None: ..."
        )
        return format_str(isort.code(text, profile="black"), mode=Mode())

    def imports(self) -> str:
        source = getmodule(self.src.type)
        case_import = (
            RenderImport(mod_name, self.src.type_name)
            if (mod_name := getattr(source, "__name__", None)) is not None
            else ""
        )
        dependency_imports = "\n".join(
            render.imports() for render in self.attr_render.values()
        )
        always_import = "from pytest_embrace import CaseArtifact\n"
        return f"{always_import}\n{case_import}\n{dependency_imports}"

    def skeleton(self) -> str:
        module_attr_hints = "\n".join(attr.hint() for attr in self.attr_render.values())
        return self.module_text(body=module_attr_hints)

    def _with_values_from_case(self, case: CaseType, hinted: bool = True) -> str:
        assignments: list[str] = []
        values = asdict(case)
        for name, attr in self.src.type_attrs.items():
            value = values[name]
            if callable(attr.dc_field.default_factory):
                default = attr.dc_field.default_factory()
            else:
                default = attr.dc_field.default

            # would've expected value == default to be true w/ trickles() but appaz not!
            if value == default or isinstance(value, Trickle):
                continue

            if isinstance(value, RenderValue):
                if match := self.funcdef_pattern.match(str(value)):
                    funcname = match["funcname"]
                    if funcname != name:
                        raise CodeGenError(
                            f"Can't render function called '{funcname}'"
                            f" for arg '{name}'. Rename the function to '{name}'"
                            " and try again."
                        )
                    assignments.append(str(value))
                    continue

                assignments.append(
                    self.attr_render[name].assignment(value, hinted=False)
                )
                continue

            assignments.append(self.attr_render[name].assignment(value, hinted=hinted))

        return "\n".join(assignments)

    def _with_values_from_list(self, values: list[CaseType]) -> str:
        typical = values[0]
        text = ", ".join(
            typical.__class__.__name__
            + "("
            + self._with_values_from_case(v, hinted=False).replace("\n", ",")
            + ")"
            for v in values
        )
        # trailing comma always
        return f"table = [{text},]"

    def _with_mixed_values(self, values: tuple[CaseType, list[CaseType]]) -> str:
        module_attrs, table = values
        header = self._with_values_from_case(module_attrs, hinted=False)
        table_content = self._with_values_from_list(table)
        return f"{header}\n\n{table_content}"

    def _expert(self, body: RenderModuleBodyValue) -> str:
        out: list[str] = []
        for item in body.contents:
            if isinstance(item, RenderValue):
                out.append(str(item))
                continue
            out.append(self.with_values(item, no_body=True))

        return "\n".join(out)


class AttrRender:
    def __init__(self, src: AttrInfo) -> None:
        self.src = src

    def imports(self) -> str:
        lookup: dict[str, list[str]] = defaultdict(list)
        for typ in _unnest_generics(self.src.dc_field.type):
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
                    getattr(typ.__class__, "__name__", ""),
                ),
            )
            if own_name == "Annotated":
                continue
            lookup[modname].append(own_name)

        return "\n".join(
            f"from {modname} import {', '.join(sorted(target))}"
            for modname, target in sorted(lookup.items(), key=itemgetter(0))
        )

    def hint(self) -> str:
        typ = (
            self.src.dc_field.type
            if self.src.annotations is None
            else self.src.annotations.type
        )
        type_str = undot_type_str(_stringify_type(typ))
        # get rid of dots and assume imports are solved
        type_str_parts = [t.lstrip("[").rstrip("]") for t in type_str.split(".")]
        if len(type_str_parts) > 1:
            type_str = type_str_parts[-1]
        comment = next(
            (
                v
                for v in getattr(self.src.annotations, "annotations", [])
                if isinstance(v, str)
            ),
            None,
        )
        text = f"{self.src.name}: {type_str}"
        if comment is not None:
            text += f"  # {comment}"
        return text

    def assignment(self, value: str | RenderValue, hinted: bool = True) -> str:
        return (
            f"{self.hint() if hinted else self.src.name}"
            f" = {value if isinstance(value, RenderValue) else repr(value)}"
        )


def _stringify_type(type: Type) -> str:
    return str(type) if not repr(type).startswith("<class") else type.__name__


def _unnest_generics(type: Type | list[Type]) -> Iterator[Type]:
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


def RenderText(text: str) -> Any:
    """Interpolate any text as Python into a @generator return."""
    return RenderValue(text)


def RenderImport(from_: str, import_: str, as_: str = "") -> Any:
    alias = as_ if as_ == "" else f" as {as_}"
    return RenderValue(f"from {from_} import {import_}{alias}")


class RenderValue:
    """Stand-in as something distinctly identifiable when using Render()."""

    def __init__(self, content: str) -> None:
        self.content = content

    def __str__(self) -> str:
        return dedent(self.content)

    def __repr__(self) -> str:
        return str(self)


# python 3.8 can't deal with list[] or | union in aliases
# (even with future import)
ModuleBodyContents = Union[List[CaseType], CaseType, RenderValue]


def RenderModuleBody(*contents: ModuleBodyContents) -> Any:
    return RenderModuleBodyValue(*contents)


class RenderModuleBodyValue:
    """Everything after the solved imports and before the `test()` function def.
    Given contents are rendered all together, separated by newlines."""

    def __init__(self, *contents: ModuleBodyContents) -> None:
        self.contents: list[ModuleBodyContents] = [*contents]
