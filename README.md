# pytest-embrace

The `pytest-embrace` plugin enables judicious, repeatable, lucid unit testing.

## Philosophy

1. Table-oriented (parametrized) tests are indespensible for productive, exhaustive unit tests.
2. Type hints and modern Python dataclasses are very good.
3. Build-time feedback is underrated.
4. Language-level APIs (like namespaces) are a honkin' great idea.
5. Code generation is *really* underrated.

## Basic Usage

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

OR you can go table-oriented and run many tests from one module––just like with `pytest.mark.parametrize`.

```python
# test_many_func.py
from conftest import Case

table = [
    Case(arg="haha", func=lambda x: x.upper(), expect="HAHA"),
    Case(arg="wow damn", func=lambda x: len(x), expect=8),
    Case(arg=object(), func=lambda x: hasattr(x, "beep"), expect=False),
]


def test(simple_case):
    ...
```

