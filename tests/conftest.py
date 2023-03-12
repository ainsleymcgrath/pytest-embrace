from __future__ import annotations

from textwrap import dedent
from types import ModuleType, SimpleNamespace
from typing import Any, Callable, Dict, Type, cast

import pytest

from pytest_embrace.case import CaseTypeInfo
from pytest_embrace.loader import ModuleInfo

pytest_plugins = "pytester"


class ModuleInfoFactory:
    @staticmethod
    def build(type: Type, *, fixture_name: str = "", **ns_kwargs: Any) -> ModuleInfo:
        default_kw: Dict[str, Any] = {}
        if "__name__" not in ns_kwargs:
            default_kw["__name__"] = "name_not_set"

        mod = cast(ModuleType, SimpleNamespace(**default_kw, **ns_kwargs))
        case_info_kwargs: Dict[str, Any] = (
            {} if fixture_name == "" else {"fixture_name": fixture_name}
        )
        return ModuleInfo(
            module=mod, case_type_info=CaseTypeInfo(type, **case_info_kwargs)
        )


@pytest.fixture
def module_info_factory() -> ModuleInfoFactory:
    return ModuleInfoFactory()


ValidPythonAssertion = Callable[[str, str], None]


@pytest.fixture
def assert_valid_text_is() -> ValidPythonAssertion:
    def do_assert(actual: str, expected: str) -> None:
        assert dedent(expected).lstrip("\n") == actual
        try:
            exec(actual, globals(), locals())  # check that it's valid
        except Exception:
            pytest.fail(f"Invalid python generated: {actual}")

    return do_assert
