from __future__ import annotations

from typing import Protocol, Type, TypeVar

import pytest

from pytest_embrace.case import CaseTypeInfo
from pytest_embrace.codegen import CaseRender

T = TypeVar("T")
S = TypeVar("S")


class RendererMaker(Protocol):
    def __call__(self, case: Type[T], *, fixture_name: str) -> CaseRender[T]:
        ...


@pytest.fixture
def make_renderer() -> RendererMaker:
    def make(case: Type[S], *, fixture_name: str) -> CaseRender[S]:
        info: CaseTypeInfo[S] = CaseTypeInfo(case, fixture_name=fixture_name)
        return CaseRender(info)

    return make
