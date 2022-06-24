# pytest-embrace :gift_heart:

[![PyPI version](https://badge.fury.io/py/pytest-embrace.svg)](https://badge.fury.io/py/pytest-embrace) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/pytest-embrace.svg)](https://pypi.python.org/pypi/pytest-embrace/) ![CI](https://github.com/ainsleymcgrath/pytest-embrace/actions/workflows/ci.yml/badge.svg)

The `pytest-embrace` plugin enables judicious, repeatable, lucid unit testing.

## Philosophy :bulb:

1. Table-oriented (parametrized) tests are indespensible.
2. Type hints and modern Python dataclasses are very good.
3. Language-level APIs (like namespaces) are a honkin' great idea.
4. Code generation is *really* underrated.
5. The wave of type-driven Python tools like Pydantic and Typer (both dependencies of this library) is very cowabunga––and only just beginning :ocean:

## Features :white_check_mark:

- [x] Completely customizable test design
- [x] Type hints everywhere
- [x] Table-oriented testing
- [x] Strongly-typed test namespaces
- [x] Highly cusomizable code generation––powered by Pep 593
- [x] Readable errors, early and often

## Basic Usage :wave:

Like any pytest plugin, `pytest-embrace` is configured in `conftest.py`.

The main ingredients are:

1. The "case" –– which can be any class decorated with `builtins.dataclasses.dataclass`.
2. The "runner" –– which is just a tricked out Pytest fixture to run assertions against your case.
3. The "caller" –– which is is another tricked out fixture that your tests will use.

```python
# conftest.py
from dataclasses import dataclass
from typing import Callable

from pytest_embrace import Embrace


@dataclass
class Case:
    arg: str
    func: Callable
    expect: str


embrace = Embrace(Case)

@embrace.register_case_runner
def run_simple(case: Case):
    result = case.func(case.arg)
    assert result == case.expect
    return result


simple_case = embrace.caller_fixture_factory('simple_case')
```

With the above conftest, you can write tests like so:

1. Make a module with attributes matching your `Embrace()`'d object
2. Request your caller fixture in normal Pytest fashion

```python
# test_func.py
arg = 'Ainsley'
func = lambda x: x * 2
expect = 'AinsleyAinsley'


def test(simple_case):
	...
```

Or you can go [table-oriented](https://dave.cheney.net/2019/05/07/prefer-table-driven-tests) and run many tests from one module––just like with `pytest.mark.parametrize`.

When `pytest-embrace` sees a `table` attribute full of case objects, it will generate a test for each member of the list.

```python
# test_many_func.py
from conftest import Case

table = [
    Case(arg="haha", func=lambda x: x.upper(), expect="HAHA"),
    Case(arg="wow damn", func=lambda x: len(x), expect=8),
    Case(arg="sure", func=lambda x: hasattr(x, "beep"), expect=False),
]


def test(simple_case):
    ...
```

:point_up_2: This runs 3 independent tests.

### Strongly Typed Namespaces :muscle:

Before even completing the setup phase of your `Embrace()`'d tests, this plugin uses [Pydantic](https://pydantic-docs.helpmanual.io/) to validate the values set in your test modules. No type hints required.

That means there's no waiting around for expensive setups before catching simple mistakes.

```python
# given this case...
arg = "Ainsley"
func = lambda x: x * 2
expect = b"AinsleyAinsley"


def test(simple_case):
    ...
```

Running the above immediately produces this error:

```python
E   pytest_embrace.exc.CaseConfigurationError: 1 invalid attr values in module 'test_wow':
E       Variable 'expect' should be of type str
```

The auxilary benefit of this feature is hardening the design of your code's interfaces––even interfaces that exist beyond the "vanishing point" of incoming data that you can't be certain of: Command line inputs, incoming HTTP requests, structured file inputs, etc.

## Code Generation :robot:

Installing `pytest-embrace` adds a flag to `pytest` called `--embrace`.

It can be used to scaffold tests based on any of your registered cases.

With the example from above, you can do this out of the box:

```shell
pytest --embrace simple_case
```

Which puts this in your clipboard:

```python
# test_more.py
from pytest_embrace import CaseArtifact
from conftest import Case

arg: str
func: "Callable"
expect: str


def test(simple_case: CaseArtifact[Case]):
    ...
```

Copypasta'd test cases like this can also be table-style: [Soon.]

```shell
pytest --embrace-table 3
```

The value passed to the `--embrace-table` flag will produce that many rows.

```python
# test_table_style.py
from pytest_embrace import CaseArtifact
from conftest import Case

table = [
    # Case(arg=..., func=..., expect=...),
    # Case(arg=..., func=..., expect=...),
    # Case(arg=..., func=..., expect=...),
]

def test(simple_case: CaseArtifact[Case]):
    ...
```

By default, each item is commented out so you don't end up with linter errors upon opening your new file.

If that's not cool, don't worry! It's configurable. :sunglasses:

### Config With Pep 593 :star2:

In order to customize the behavior of your test cases, `pytest-embrace` :flushed: embraces :flushed:  the new `Annotated` type.

> :information_source:
> If you've never heard of Pep 593 or `Annotated`, the **tl;dr** is that `Annotated[<type>, ...]` takes any number of arguments after the first one (the actual hint) that developers (me) can use at rumtime.
>
> **Also this only works on Python >3.8.**

The `pytest_embrace.anno` namespace provides a number of utilities for controlling test parsing and code generation via `Annotated`.

#### Comments in Generated Tests :pencil:

Here's an example of using `anno.Comment` to put comments in generated test suites:

```python
from dataclasses import dataclass

from pytest_embrace import Embrace, anno


@dataclass
class AnnotatedCase:
    name: Annotated[str, anno.Comment("This is ... pretty cool.")]


embrace = Embrace(AnnotatedCase)


@embrace.register_case_runner
def run(case: AnnotatedCase, fix: str) -> None:
    pass


anno_case = embrace.caller_fixture_factory("anno_case")
```

Calling the generation utility...

```shell
pytest --embrace anno_case
```

Gets you this:

```python
from pytest_embrace import CaseArtifact

import AnnotatedCase from conftest


name: str  # This is ... pretty cool.


def test(anno_case: CaseArtifact[AnnotatedCase]) -> None:
    ...
```



## Complexity :lollipop:

### Table Cases vs Module Cases :balance_scale:

As we've seen `pytest-embrace` can produce and execute 2 types of cases:

1. *"Module cases"* where a test is a single file
2. *"Table cases"* where the  `table` attribute generates as many tests as there are members of the `table` list.

There are pros and cons to each approach:

|                          | **Table**                                                    | **Module**                                                   |
| -----------------------: | ------------------------------------------------------------ | ------------------------------------------------------------ |
|         **Pros** :smile: | Everything is in one place.<br /><br />The format is a bit more familiar to veteran `parametrize` users.<br /><br />Writing many cases in one file at once can be easier than jumping around. | It's easier to get going with module tests generated by `--embrace`.<br /><br />A directory full of tests is more discoverable than a big literal list of tests.<br /><br />You can select one test at a time with modules. |
| **Cons** :frowning_face: | A gigantic list of cases can get out of hand and become very difficult to grok.<br /><br />Over time, if the expectation of 1 case diverges from its siblings, things can get messy.<br /><br />Repetitive tests (e.g. they all share similar default attributes) are ugly. | Many developers detest "death by 1000 files."<br /><br />Sharing configuration among similar tests requires finesse.<br /><br />Repetitive tests can be hard to name well and keep track of. |

This framework was born from several iterations of essentially the same concept across a couple repos at [Amper](https://www.amper.xyz/) and in my hobby projects. Some versions supported the table, some did not, and some did an opinionated mix––where certain module-level attributes could "trickle down" to cases or certain attributes were *only* allowed at the module level and applied to all table cases.

To address the module-vs-table tension, `pytest-embrace` provides a utility to design tests that freely mix table and module style: `trickles()`.

Just use it as the default value for attributes of your case where you would like the module-level attribute to "trickle down" to cases in tables.

By default, table cases can set that attribute themselves to override the module value. If that's not ok, pass `no_override=True` and then overriding will throw an error.

```python
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


@embrace.register_case_runner
def my_runner(case: TrickleCase) -> None:
    pass


trickle_case = embrace.caller_fixture_factory("trickle_case")
```

And here's how that looks in a test:

```python
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
```

And this one would throw an error:

```python
from conftest import TrickleCase


table = [
    TrickleCase(
        snack="do you have any dates?",
        ounces_of_beverage = 1
    ),
]


def test(trickle_case):
    ...
```

### Config With Pep 593 :star2:

We've already seen `anno.Comment()` for manipulating code generation.

But annotations can also control the setup phase of `Embrace()`'d tests.

#### Deriving Attributes from Filenames :crystal_ball:

The `DeriveFromFileName` object in the `anno` namespace allows you to lift the determination of case attributes out of the case and *into the name of the test file.*

Here's how it works:

```python
# conftest.py
from dataclasses import dataclass

from pytest_embrace import Embrace, anno


@dataclass
class DeriveCase:
    name: Annotated[str, anno.DeriveFromFileName()]


embrace = Embrace(DeriveCase)


@embrace.register_case_runner
def run(case: AnnotatedCase) -> None:
    pass


derive_case = embrace.caller_fixture_factory("derive_case")
```

The default derivation simply extracts the substring after `test_` in your module's name.

So, using `derive_case`, you don't need to put `name` in the module.

```python
# test_something.py
from conftest import DeriveCase


def test(derive_case: CaseArtifact[DeriveCase]):
    assert derive_case.case.name == 'something'
```
