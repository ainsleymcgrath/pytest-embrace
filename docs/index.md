# Introduction

![Image title](logotype.svg)

> _Reject boilerplate. Embrace complexity._

`pytest-embrace` is a Pytest-plugin-cum-metaframework that facilitates structured, iterative, type-driven unit testing.

This plugin's long-term goal is to be the [FastAPI](https://fastapi.tiangolo.com/) of [Pytest](https://docs.pytest.org/en/7.1.x/) plugins.

## Why should you use `pytest-embrace`?

Because you like:

- Functional & unit testing with Pytest
- Dataclasses & type hints
- Generating useful copypasta
- Type safety

If you know how to use dataclasses and Pytest fixtures, you're ready to use `pytest-embrace`.

## Basic Usage
As is tradition:

```bash
pip install pytest-embrace  # use a virtualenv in your preferred fashion
```

### Configuring the framework

Like any pytest plugin, `pytest-embrace` is configured in `conftest.py`.

The main ingredients are:

1. The **"case"** –– which can be any class decorated with `builtins.dataclasses.dataclass`.
2. The **"runner"** –– which is just a tricked out Pytest fixture to run assertions against your case.
3. The **"caller"** –– which is is another tricked out fixture that your tests will use. *The caller is the entrypoint to your test functionatlity.*

```python
# conftest.py
from dataclasses import dataclass
from typing import Any, Callable

from pytest_embrace import Embrace


@dataclass
class Case:  # (1)
    arg: str
    func: Callable
    expect: Any


embrace = Embrace(Case)  # (2)


@embrace.register_case_runner  # (3)
def run_simple(case: Case):
    result = case.func(case.arg)
    assert result == case.expect
    return result


simple_case = embrace.caller_fixture_factory("simple_case")  # (4)
```

1.    **A dataclass describes the schema of your test modules.**<br><br>In this case, modules will need to define the attributes (variables) `arg`, `func`, and `expect`.
2.    **Create an `Embrace()` instance.**<br><br>The methods exposed on this class define the *behavior* and *identity* of tests who implement the schema.
3.    **Register a "case runner" to define test *behavior.***<br><br>The "case runner" is a Pytest fixture like any other, with special access to the values in a test module.
4.    **Create a "caller fixture" to give this new kind of test an *identity.***<br><br>The "caller fixture" is what you'll request in the signature of Pytest tests. It's also the name seen/used in `--embrace` CLI utils.

The `simple_case` fixture is the identity of this new flavor of test you've created.

You *could* just go a module and reference `simple_case` in a test function or....

You could just run this:

```shell
pytest --embrace test_simple
```

And then simply paste the output (it's already in your clipboard) into a new file.

```python
# test_wow.py
from typing import Any, Callable  # (1)

from pytest_embrace import CaseArtifact

from conftest import Case

arg: str
func: Callable
expect: Any


def test(simple_case: CaseArtifact[Case]) -> None:
    ...
```

1.    😮 Note how Embrace figured out the right imports for types!

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

And if you write a test that doesn't conform to the shape of your dataclass...

```python
arg = b"Accidental bytes"
func = lambda x: x.upper() + "!!"
expect = "ACCIDENTAL BYTES!!"
```

You get reprimanded right away.

```shell
E   pytest_embrace.exc.CaseConfigurationError: 1 invalid attr values in 'test_wow':
E       Variable/Arg 'arg' should be of type str
```

## Anything is possible

The pattern employed by `pytest-embrace` could technically be applied to any unit tests.

In practice, however, it does best when:

- You have enormously tall [parametrized](https://docs.pytest.org/en/7.1.x/how-to/parametrize.html#parametrize) tests that have become hard to grok and maintain.
- You are testing a consistent interface at a high level (think API endpoints) that rely on external state (like databases).
  - And you've realized over time that all those tests are _pretty much_ the same... but nuance makes parametrizing hard and you resign yourself to long breadcrumb trails of fixtures that may-or-may-not actually be used by your tests and just like... 😤 ugh.
- You like type safety, generating code, iterating quickly, testing exhaustively, and being DRY.

## Learn More

Check out the [feature-by-feature guide](./usage/index.md).
