from __future__ import annotations

import json
from textwrap import dedent
from typing import Any

from pytest_embrace.case import CaseTypeInfo
from pytest_embrace.embrace import CaseTypeRegistry
from pytest_embrace.exc import CodeGenError


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

        if self.generator_name is None:
            return self.case_type.render_skeleton()

        try:
            generator = self.case_type.generators[self.generator_name]
        except KeyError as e:
            raise TypeError(f"No custom generator named {self.generator_name}") from e

        case = generator(**self.generator_kwargs)
        return self.case_type.render_with_values_from(case)


def txt(text: str) -> Any:
    """Interpolate any text as Python into a @generator return."""
    return RenderValue(text)


class RenderValue:
    """Stand-in as something distinctly identifiable when using txt()."""

    def __init__(self, content: str) -> None:
        self.content = content

    def __str__(self) -> str:
        return dedent(self.content)
