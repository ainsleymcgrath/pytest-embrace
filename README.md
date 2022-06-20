# pytest-embrace :gift_heart:

The `pytest-embrace` plugin enables judicious, repeatable, lucid unit testing.

## Philosophy :bulb:

1. Table-oriented (parametrized) tests are indespensible.
2. Type hints and modern Python dataclasses are very good.
3. Language-level APIs (like namespaces) are a honkin' great idea.
4. Code generation is *really* underrated.

## Features :white_check_mark:

- [x] Completely customizable test design
- [x] Type hints everywhere
- [x] Table-oriented testing
- [ ] Code generation
- [ ] Reporting / discovery tools
- [ ] Pep 593 powered customization

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

from pytest_embrace import CaseArtifact, Embrace


@dataclass
class Case:
    arg: str
    func: Callable
    expect: str


embrace = Embrace(Case)

@embrace.register_runner
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

Or you can go table-oriented and run many tests from one module––just like with `pytest.mark.parametrize`.

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

## Code Generation :robot:

Installing `pytest-embrace` gives you access to a CLI called `embrace`.

It can be used to scaffold tests based on any of your registered cases.

With the example from above, you can do this out of the box:

```shell
embrace simple_case --path test_more.py
```

Resulting in:

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

## Pep 593 :star2:

In order to customize the behavior of your test cases, `pytest-embrace` ...embraces... the new `Annotated` type.

> If you've never heard of Pep 593 or `Annotated`, the **tl;dr** is that `Annotated[<type>, ...]` takes any number of arguments that developers (me) can use at rumtime.

The `pytest_embrace.anno` namespace provides a number of utilities for controlling test parsing and generation via `Annotated`.

```python
from dataclasses import dataclass
from typing import Annotations

from pytest_embrace import anno


@dataclass
class FancyCase:
    prop_1: Annotated[str, anno.Trickle()]
    prop_2: Annotated[list[int], anno.OnlyWith('prop_3')]
    prop_3: dict[str, set]
```
