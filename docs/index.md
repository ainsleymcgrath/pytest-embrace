# Introduction

![Image title](logotype.svg)

> _Reject boilerplate. Embrace complexity._

`pytest-embrace` is a Pytest plugin-slash-metaframework offering:

- Convenient **abstractions for parametrized tests**
- Great DX with **type hints everywhere**
- **[Code generation](#codegen)** with low effort

This plugin's long-term goal is to be the [FastAPI](https://fastapi.tiangolo.com/) of [Pytest](https://docs.pytest.org/en/7.1.x/) plugins.

## Basic Usage

If you know how to use dataclasses and Pytest fixtures, you're ready to use `pytest-embrace`.

As is tradition:

```bash
pip install pytest-embrace  # use a virtualenv in your preferred fashion
```

### Configure your test

Like any pytest plugin, `pytest-embrace` is configured in `conftest.py`.

There are 2 ingredients

1. The **"case"** –– which can be any class decorated with `builtins.dataclasses.dataclass`.
2. The **"fixture"** –– which is just a tricked out Pytest fixture to run assertions against your case.

```python
# conftest.py
from dataclasses import dataclass
from typing import Any, Callable

from pytest_embrace import Embrace


@dataclass
class Case:  # (1)
    arg: str
    func: Callable[[str], Any]
    expect: Any


embrace = Embrace(Case)  # (2)


@embrace.fixture  # (3)
def simple_case(case: Case):
    result = case.func(case.arg)
    assert result == case.expect
    return result
```

1.  **A dataclass describes the schema of your test modules.**<br><br>In this case, modules will need to define the attributes (variables) `arg`, `func`, and `expect`.
2.  **Create an `Embrace()` instance.**<br><br>The methods exposed on this class define the _behavior_ and _identity_ of tests who implement the schema.
3.  **Create a fixture to run the tests.**<br><br>This fixture is just like any other, but with some under-the-hood stuff to enable code-generation, validation, discoverability, and module-parsing.

### Generate a test

The `simple_case` fixture is the identity of this new flavor of test you've created.

You _could_ just make a module and reference `simple_case` in a test function or....

You could run this:

```shell
pytest --embrace simple_case
```

And then paste the output (it's already in your clipboard) into a new file.

```python
# test_wow.py
from typing import Any, Callable  # (1)

from pytest_embrace import CaseArtifact

from conftest import Case

arg: str
func: Callable[[str], Any]
expect: Any


def test(simple_case: CaseArtifact[Case]) -> None:
    ...
```

1.  😮 Note how Embrace figured out the right imports for types!

### Run the test

Fill in the values (with the comfort of autocomplete / editor help):

```python
from pytest_embrace import CaseArtifact
from conftest import Case


arg = "wow"
func = lambda x: x.upper() + "!!"
expect = "WOW!!"


def test(simple_case: CaseArtifact[Case]) -> None:
    ...
```

And run it by calling `pytest`.

```shell
============================= test session starts ==============================
platform darwin -- Python 3.10.4, pytest-7.1.2, pluggy-1.0.0
rootdir: /Users/ains/repos/tso/embrace
plugins: embrace-1.0.1
collected 1 item

test_wow.py .                                                            [100%]

============================== 1 passed in 0.01s ============================
```

### 🚀 Powerful Code Generation {#codegen}

Skeleton tests are fine, but `Embrace()` offers another decorator: `@generator`.

**`pytest-embrace` code generators allow you to dynamically create tests via command-line input.**

```python
@embrace.generator
def my_gen(arg, expect, func):  # (1)
    return Case(
        arg=arg,
        func=RenderText(func),  # (2)
        expect=expect,
    )
```

1.  Arguments to the function will be provided via CLI and parsed as JSON.
1.  `RenderText(value)` lets you interpolate any valid python expression into your tests.

With a slightly different form of argument to `--embrace`, you can provide `arg`, `expect`, and `func` and eliminate boilerplate completely.

```shell
pytest --embrace 'simple_case:my_gen arg=foo expect=3 func=len'
```

The above will generate this:

```python
from collections.abc import Callable
from typing import Any

from pytest_embrace import CaseArtifact

from conftest import Case

arg = "foo"
func = len
expect = 3


def test(simple_case: CaseArtifact[Case]) -> None:
    ...
```

This only scratches the surface of `@generator` and code-rendering utilities.

## Validation for Free

If you write a test that doesn't conform to the shape of your dataclass...

```python
arg = b"Accidental bytes"
func = lambda x: x.upper() + "!!"
expect = "ACCIDENTAL BYTES!!"
```

you get reprimanded right away.

```shell
E   pytest_embrace.exc.CaseConfigurationError: 1 invalid attr values in 'test_wow':
E       Variable/Arg 'arg' should be of type str
```

## When would I use this?

The pattern employed by `pytest-embrace` could technically be applied to any unit tests.

In practice, however, it does best when:

- You have enormously tall [parametrized](https://docs.pytest.org/en/7.1.x/how-to/parametrize.html#parametrize) tests that have become hard to grok and maintain.
- You are testing a consistent interface at a high level (think API endpoints) that rely on external state (like databases).
  - And you've realized over time that all those tests are _pretty much_ the same... but nuance makes parametrizing hard and you resign yourself to long breadcrumb trails of fixtures that may-or-may-not actually be used by your tests and just like... 😤 ugh.
- You like type safety, generating code, iterating quickly, testing exhaustively, and being DRY.

## Learn More

Check out the [feature-by-feature guide](./usage/index.md).
