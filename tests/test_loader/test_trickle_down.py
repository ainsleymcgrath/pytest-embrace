from __future__ import annotations

from dataclasses import dataclass
from typing import List

from pytest_embrace import trickles
from pytest_embrace.loader import load
from tests.conftest import ModuleInfoFactory


@dataclass
class AnnotatedWithTrickleCase:
    bar: int
    foo: List[str] = trickles()


def test_value_trickles_down(module_info_factory: ModuleInfoFactory) -> None:
    target = module_info_factory.build(
        AnnotatedWithTrickleCase,
        foo=["hey", "sup"],
        table=[
            AnnotatedWithTrickleCase(bar=55),
            AnnotatedWithTrickleCase(bar=66, foo=["woah there"]),
            AnnotatedWithTrickleCase(bar=66, foo=[]),
        ],
    )
    loaded = load(target)
    assert loaded[0].foo == ["hey", "sup"], (
        "When a table member isn't given an arg,"
        " it inherits it from the parent case."
    )
    assert loaded[1].foo == ["woah there"], "Table cases can override their parents"
    assert (
        loaded[2].foo == []
    ), "Table cases can override their parents with falsey values"
