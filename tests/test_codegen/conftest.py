from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Type, TypeVar

import pytest

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

from pytest_embrace.case import CaseTypeInfo
from pytest_embrace.codegen import CaseRender

T = TypeVar("T", bound="DataclassInstance")
S = TypeVar("S", bound="DataclassInstance")


class RendererMaker(Protocol):
    def __call__(self, case: Type[T], *, fixture_name: str) -> CaseRender[T]:
        ...


@pytest.fixture
def make_renderer() -> RendererMaker:
    def make(case: Type[S], *, fixture_name: str) -> CaseRender[S]:
        info: CaseTypeInfo[S] = CaseTypeInfo(case, fixture_name=fixture_name)
        return CaseRender(info)

    return make
