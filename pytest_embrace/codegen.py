from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import asdict
from inspect import getmodule
from operator import itemgetter
from textwrap import dedent
from typing import Any, Generic, Type, get_args, get_origin

import isort
from black import format_str
from black.mode import Mode
from pyperclip import sys

from pytest_embrace.case import AttrInfo, CaseCls, CaseType, CaseTypeInfo
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
                # a string is expected to fail since it doesn't come in quoted
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

        case = generator(**self.generator_kwargs)
        # return render_with_values(case_type, values)
        return renderer.with_values(case)


class CaseRender(Generic[CaseCls]):
    def __init__(self, src: CaseTypeInfo[CaseCls]):
        self.src = src
        self.attr_render = {
            name: AttrRender(info) for name, info in self.src.type_attrs.items()
        }

    def module_text(self, *, body: str = "") -> str:
        return format_str(
            f"{self.imports()}\n{body}\n"
            f"def test({self.src.caller_name}: CaseArtifact[{self.src.type_name}])"
            " -> None: ...",
            mode=Mode(),
        )

    def imports(self) -> str:
        source = getmodule(self.src.type)
        case_import = (
            f"from {mod_name} import {self.src.type_name}"
            if (mod_name := getattr(source, "__name__", None)) is not None
            else ""
        )
        dependency_imports = "\n".join(
            render.imports() for render in self.attr_render.values()
        )
        always_import = "from pytest_embrace import CaseArtifact\n"
        return isort.code(
            f"{always_import}\n{case_import}\n{dependency_imports}", profile="black"
        )

    def skeleton(self) -> str:
        module_attr_hints = "\n".join(attr.hint() for attr in self.attr_render.values())
        return self.module_text(body=module_attr_hints)

    def with_values(self, case: CaseType) -> str:
        assignments: list[str] = []
        values = asdict(case)
        for name, attr in self.src.type_attrs.items():
            value = values[name]
            if callable(attr.dc_field.default_factory):
                default = attr.dc_field.default_factory()
            else:
                default = attr.dc_field.default

            if value == default:
                continue

            if isinstance(value, RenderValue):
                assignments.append(str(value))
                continue

            assignments.append(self.attr_render[name].assignment(value))

        return self.module_text(body="\n".join(assignments))


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
                    getattr(
                        typ.__class__,
                        "__name__",
                    ),
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

    def assignment(self, value: str, hinted: bool = True) -> str:
        return f"{self.hint() if hinted else self.src.name} = {repr(value)}"


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


def txt(text: str) -> Any:
    """Interpolate any text as Python into a @generator return."""
    return RenderValue(text)


# def RenderText(content: str) -> Any:
#     return RenderValue(content)


# def RenderModuleBody(*contents: str | "CaseType" | list["CaseType"]) -> Any:
#     return InnerTestModuleBody(*contents)


class RenderValue:
    """Stand-in as something distinctly identifiable when using txt()."""

    def __init__(self, content: str) -> None:
        self.content = content

    def __str__(self) -> str:
        return dedent(self.content)


class InnerTestModuleBody:
    """Everything after the solved imports and before the `test()` function def.
    Given contents are rendered all together, separated by newlines."""

    def __init__(self, *contents: str) -> None:
        self.contents: list[str] = [*contents]

    def __str__(self) -> str:
        return "\n".join(map(txt, self.contents))


# '''
# RenderModuleBody(
#     RenderText("_x = 12  # foobar"),  # not an attr of test
#     Case(arg=Render("{'foo': 'bar'}")),  # top-level attr
#     [Case(expect=1), Case(expect=2)],  # rendered as `table`
#     RenderText(  # multiline content
#         """
#         def func():
#             return _x
#         """
#     ),
# )'''
