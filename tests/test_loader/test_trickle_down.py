from dataclasses import dataclass
from typing import List

from pytest_embrace import trickles
from pytest_embrace.loader import handle_table_trickle_down

from .utils import module_factory


@dataclass
class AnnotatedWithTrickleCase:
    bar: int
    foo: List[str] = trickles()


def test_value_trickles_down() -> None:
    mod = module_factory(
        foo=["hey", "sup"],
        table=[
            AnnotatedWithTrickleCase(bar=55),
            AnnotatedWithTrickleCase(bar=66, foo=["woah there"]),
            AnnotatedWithTrickleCase(bar=66, foo=[]),
        ],
    )
    loaded = handle_table_trickle_down(AnnotatedWithTrickleCase, mod)
    assert loaded[0].foo == ["hey", "sup"], (
        "When a table member isn't given an arg,"
        " it inherits it from the parent case."
    )
    assert loaded[1].foo == ["woah there"], "Table cases can override their parents"
    assert (
        loaded[2].foo == []
    ), "Table cases can override their parents with falsey values"
