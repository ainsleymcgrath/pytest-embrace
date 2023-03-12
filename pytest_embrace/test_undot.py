from __future__ import annotations

import pytest

from pytest_embrace.undot import undot_type_str


@pytest.mark.parametrize(
    "given, expected",
    [
        ("foo", "foo"),
        ("foo.bar", "bar"),
        # skipping this one since it's not really a valid type
        ("[foo.bar]", "[bar]"),
        ("foo.bar.baz.buzz.whizz", "whizz"),
        ("foo[baz.bar, bizz.bozz]", "foo[bar, bozz]"),
        ("typing.Callable[[str], typing.Any]", "Callable[[str], Any]"),
        (
            "typing.Callable[[fizz.buzz, fonz.bonz], buzz.bazz]",
            "Callable[[buzz, bonz], bazz]",
        ),
    ],
)
def test(given: str, expected: str) -> None:
    actual = undot_type_str(given)
    assert expected == actual
