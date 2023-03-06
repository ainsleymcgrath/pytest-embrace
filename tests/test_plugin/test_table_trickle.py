from __future__ import annotations

import pytest

from .utils import make_autouse_conftest

_ = make_autouse_conftest(
    """
    from dataclasses import dataclass
    import pytest

    from pytest_embrace import  Embrace
    from pytest_embrace.case import CaseArtifact, trickles


    @dataclass
    class TrickleCase:
        snack: str
        beverage: str = trickles()
        ounces_of_beverage: int = trickles(no_override=True)


    embrace = Embrace(TrickleCase)


    @embrace.fixture
    def trickle_case(case: TrickleCase) -> None:
        pass"""
)


SIMPLE_TEST_MODULE = """
from conftest import TrickleCase

beverage = 'just water, thanks'
ounces_of_beverage = 16

table = [
    TrickleCase(snack='do you have any dates?'),
    TrickleCase(snack="I'm stuffed! No thanks.", beverage='espresso')
]

def test(trickle_case):
    bev = trickle_case.case.beverage
    snack = trickle_case.case.snack

    if bev == 'just water, thanks':
        assert snack == 'do you have any dates?'
    elif bev == 'espresso':
        assert snack == "I'm stuffed! No thanks."
    else:
        raise Exception("We should never get here.")
"""


def test_single(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(SIMPLE_TEST_MODULE)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(passed=2)


TEST_MODULE_ESCHEWS_TABLE = """
from conftest import TrickleCase

beverage = 'seriously just water, please.'
snack = '100,000 pistachios'
ounces_of_beverage = 1


def test(trickle_case):
    ...
"""


def test_no_table(pytester: pytest.Pytester) -> None:
    """You don't _have_ to use a table if you use trickles()."""
    pytester.makepyfile(TEST_MODULE_ESCHEWS_TABLE)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(passed=1)


TEST_MODULE_ESCHEWS_TRICKLING = """
from conftest import TrickleCase


table = [
    TrickleCase(
        snack="do you have any dates?",
        beverage="just water, thanks",
        ounces_of_beverage=12,
    ),
    TrickleCase(
        snack="I'm stuffed! No thanks.",
        beverage="espresso",
        ounces_of_beverage=2,
    ),
]


def test(trickle_case):
    ...
"""


def test_no_trickle(pytester: pytest.Pytester) -> None:
    """You don't need to set the trickle attr if every test sets it."""
    pytester.makepyfile(TEST_MODULE_ESCHEWS_TRICKLING)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(passed=2)


TEST_MODULE_MAKES_MISTAKE = """
from conftest import TrickleCase

ounces_of_beverage = 1000000

table = [
    TrickleCase(
        snack="do you have any dates?",
        beverage="just water, thanks",
    ),
    TrickleCase(
        snack="I'm stuffed! No thanks.",
        beverage="espresso",
        ounces_of_beverage=2,
    ),
]


def test(trickle_case):
    ...

"""


def test_cant_trickle_no_override(pytester: pytest.Pytester) -> None:
    """Ok... If you have a trickle that is `no_override`, you _can_
    set it on every test (like the previous test) but you _can't_
    set it at both levels."""
    pytester.makepyfile(TEST_MODULE_MAKES_MISTAKE)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(errors=1)
    outcome.stdout.fnmatch_lines(
        # closing brackets are a problem for some reason
        "*Trickle-down attribute 'ounces_of_beverage cannot be overridden in table[1*"
    )


# beverage is not set anywhere
TEST_MODULE_UNSET_BOTH_PLACES = """
from conftest import TrickleCase


table = [
    TrickleCase(
        snack="do you have any dates?",
        ounces_of_beverage=1
    ),
]


def test(trickle_case):
    ...
"""


def test_cant_be_totally_missing(pytester: pytest.Pytester) -> None:
    """If a trickle attr isn't set at top level and also not in a case,
    that aint ok."""
    pytester.makepyfile(TEST_MODULE_UNSET_BOTH_PLACES)
    outcome = pytester.runpytest()
    outcome.assert_outcomes(errors=1)
    outcome.stdout.fnmatch_lines(
        [
            # closing brackets are a problem for some reason
            "*'beverage' is unset at the module level and in table[0*"
        ]
    )
