# From Modules to Tables to Both

`pytest-embrace` allows you to define tests as Python _modules_ whose schemas are defined as dataclasses.

So far, more tests (and test coverage) just means more files. While this has benefits (most notably discoverability) it also can become tiresome, especially when testing the exact same functionality with a variety of different scenarios.

## Table Tests

Luckily the framework has a special behavior when it encounters a variable named `table` in your test modules: If the `table` refers to a list of instances of the dataclass you registered with `Embrace`, the framework will use `pytest.mark.parametrize` to run an independent test for each member of the list.

The two tests that were written as two files in the previous section can be refactored to this:

```python title="test_is_bread.py"
from conftest import CrudTestCase
from crud import is_bread

table = [
    CrudTestCase(
        seed_data=[
            ("mirth", False, "feeling", "prefontal cortex", 5),
            ("fear", False, "feeling", "prefontal cortex", 0),
            ("croissant", True, "food", "france", 4),
        ],
        crud_func=is_bread,
        args=("mirth",),
        assert_return=False,
        should="Mirth is a feeling, not bread.",
    ),
    CrudTestCase(
        seed_data=[
            ("mirth", False, "feeling", "prefontal cortex", 5),
            ("fear", False, "feeling", "prefontal cortex", 0),
            ("croissant", True, "food", "france", 4),
        ],
        crud_func=is_bread,
        args=("croissant",),
        assert_return=True,
        should="A croissant is tasty bread.",
    ),
]


def test(crud_case):
    ...
```

This is cool, but there's still a good bit of repetition, which we've been trying to avoid.

We _could_ lift some stuff into `SCREAMING_CONSTANTS` but that's not _really_ a solution, it's just a well-liked bandaid. Good for preventing bugs, but not that helpful for our brains.

Luckily, there is a solution!

### Data Trickles Down

Let's take it way back to the definition of `CrudTestCase`.

```python title="conftest.py"
from typing import Callable, Any
from pytest_embrace import trickles


@dataclass
class CrudTestCase:
    seed_data: list[tuple[Any, ...]]
    crud_func: Callable[..., Any]
    args: tuple[Any, ...]
    assert_return: Any
    should: str
```

While `pytest-embrace` doesn't make you inherit from any kind of opinionated base class, it does come with some utilities for layering framework-specific behaviors into your cases.

The first one is called `trickles()`. It's a wrapper around [`dataclasses.field`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field).

When you assign it to a property in your dataclass, it tells the framework to treat it specially:

- When a field on your test case class is assigned to `trickles()`...
- And you define a module with a `table`...
- Then at runtime, `pytest-embrace` will look for any "trickled" attributes in _module scope_ before looking at the objects in `table`.
- If it finds that any table members have not been passed values for "trickled" attributes, those cases simply use the module-scoped value.

So, let's make `crud_func` and `seed_data` trickle:

```python title="conftest.py"
from typing import Callable, Any
from pytest_embrace import trickles


@dataclass
class CrudTestCase:
    args: tuple[Any, ...]
    assert_return: Any
    should: str
    seed_data: list[tuple[Any, ...]] = trickles()
    crud_func: Callable[..., Any] = trickles()
```

Now, we can make the test suite like this:

```python title="test_is_bread.py"
from conftest import CrudTestCase
from crud import is_bread

seed_data = [
    ("mirth", False, "feeling", "prefontal cortex", 5),
    ("fear", False, "feeling", "prefontal cortex", 0),
    ("croissant", True, "food", "france", 4),
]
crud_func = is_bread

table = [
    CrudTestCase(
        args=("mirth",),
        assert_return=False,
        should="Mirth is a feeling, not bread.",
    ),
    CrudTestCase(
        args=("croissant",),
        assert_return=True,
        should="A croissant is tasty bread.",
    ),
]


def test(crud_case):
    ...
```

**With this change, each member of `table` concerns itself exclusively with the things that are unique to that test, and the things they have in common are mentioned only one time.** How DRY!

By default, individual cases can override the module-scope value.

We can make the first test fail by overriding its `crud_func`:

```python title="test_is_bread.py"
from conftest import CrudTestCase
from crud import is_bread

seed_data = [
    ("mirth", False, "feeling", "prefontal cortex", 5),
    ("fear", False, "feeling", "prefontal cortex", 0),
    ("croissant", True, "food", "france", 4),
]
crud_func = is_bread

def _evil_func(*_):
    return "FAILURE"

table = [
    CrudTestCase(
        args=("mirth",),
        assert_return=False,
        should="Mirth is a feeling, not bread.",
    ),
    CrudTestCase(
        crud_func=_evil_func,  # <- uh oh.
        args=("croissant",),
        assert_return=True,
        should="A croissant is tasty bread.",
    ),
]


def test(crud_case):
    ...
```

### Being Strict

One of the emergent downsides of table tests is that they're very prone to bloat.

It's easy to copypaste a member from an existing table and add it to the bottom. Easy!

But this library exists to keep you organized! In the example above, `seed_data` and `crud_func` both trickle down. The former makes sense: It certainly stands to reason that `is_bread` should be tested with different preexisting data. As for `crud_func`... it's pretty nice to have one file concern itself with one API. Letting in random functions would totally kill the vibe and let this file get unweildy.

The _only_ argiment that `trickles` takes and `field` does not is: `no_override`.

```python title="conftest.py"
@dataclass
class CrudTestCase:
    args: tuple[Any, ...]
    assert_return: Any
    should: str
    seed_data: list[tuple[Any, ...]] = trickles()
    crud_func: Callable[..., Any] = trickles(no_override=True)
```

With `no_override=True`, the second test above becomes illegal. When you run the tests now, you'll get a `CaseConfigurationError`.

## An Aside on Test Output

If you ran that last example, you probably saw some pretty unruly test output:

```shell
E   pytest_embrace.exc.CaseConfigurationError: In table[1]:CrudTestCase(args=('croissant',), assert_return=True, should='A croissant is tasty bread.', seed_da
ta=[('mirth', False, 'feeling', 'prefontal cortex', 5), ('fear', False, 'feeling', 'prefontal cortex', 0), ('croissant', True, 'food', 'france', 4)], crud_fun
c=<function <lambda> at 0x105145d80>), 'crud_func' is set, but 'crud_func' is defined at the module level as well and configured as as no_override. Accept the
 default or change the config.
```

What you're seeing is just the default `str` of `CrudTestCase`. Defining `__str__` to something pretty drastically improves things:

```python title="conftest.py"
@dataclass
class CrudTestCase:
    args: tuple[Any, ...]
    assert_return: Any
    should: str  # assertion message
    seed_data: list[tuple[Any, ...]] = trickles()
    crud_func: Callable[..., Any] = trickles(no_override=True)

    def __str__(self) -> str:
        return f"{self.crud_func.__name__}{self.args} -> {self.assert_return}"
```

The failure looks much better:

```shell
E   pytest_embrace.exc.CaseConfigurationError: In table[1]:_evil_func('croissant',) -> True,
'crud_func' is set, but 'crud_func' is defined at the module level as well and configured as as no_override. Accept the default or change the config.
```

And running `pytest -v` after fixing the config error shows each member of the `table` nicely.

```
test_is_bread_table.py::test[is_bread('mirth',) -> False] PASSED                                                                                       [ 50%]
test_is_bread_table.py::test[is_bread('croissant',) -> True] PASSED                                                                                   [100%]
```
