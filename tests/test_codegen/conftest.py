from __future__ import annotations

from typing import Any, Protocol, Type, TypeVar

import pytest

from pytest_embrace.case import CaseTypeInfo
from pytest_embrace.codegen import CaseRender

T = TypeVar("T")


class RendererMaker(Protocol):
    def __call__(self, case: Type[T], *, fixture_name: str) -> CaseRender[T]:
        ...


@pytest.fixture
def make_renderer() -> RendererMaker:
    def make(case: Type[T], *, fixture_name: str) -> CaseRender[T]:
        info: CaseTypeInfo[T] = CaseTypeInfo(case, fixture_name=fixture_name)
        return CaseRender(info)

    return make


def make_renderer_fixture(case_type: Type[T], *, fixture_name: str) -> Any:
    @pytest.fixture
    def fix(make_renderer: RendererMaker) -> Any:
        return make_renderer(case_type, fixture_name=fixture_name)

    return fix
