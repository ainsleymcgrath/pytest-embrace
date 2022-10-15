# Naming: From Liability to Asset

> There are only two hard things in Computer Science: cache invalidation and naming things.
>
> -- Phil Karlton (via [Martin Fowler](https://martinfowler.com/bliki/TwoHardThings.html))

In the last section, using `trickles(no_override=True)` allowed us to restrict the test case we've been working on to testing one function at a time. This can help keep tests organized and focused, as all the tests that have to do with some function are all bundled together, and different functions can get their own files.

But there's a major drawback here: naming. Right now it's fine. `is_bread()` is tested in `test_is_bread.py`. But what if we brilliantly renamed the function to `affirm_breadness`? Discoverability would wither and life would grow confusing.

**`pytest_embrace` has another feature, similar to `trickles()`, that helps use filenames as data: `derive_from_filename()`. It is** another wrapper around `dataclasses.field`. By default, it extracts the substring in the filename that follows the word `test_`.

That means for `test_is_bread.py`, we could extract `is_bread`, which is a good start, but we need a specific function, not a string.

Luckily, `derive_from_filename` takes a `parse` argument that lets us take that substring and do anything we want with it, ultimately returning any value.

In our case, it can be used to find the right `crud` function based on the name of the test file.

```python title="test_is_bread.py"
import crud  # the namespace we test against


@dataclass
class CrudTestCase:
    args: tuple[Any, ...]
    assert_return: Any
    should: str  # assertion message
    seed_data: list[tuple[Any, ...]] = trickles()

    # tada!
    crud_func: Callable[..., Any] = derive_from_filename(
        parse=lambda x: getattr(crud, x)
    )

    def __str__(self) -> str:
        return f"{self.crud_func.__name__}{self.args} -> {self.assert_return}"
```

And we can remove the `crud_func` declaration from the test file.

```python title="test_is_bread.py"
from conftest import CrudTestCase

seed_data = [
    ("mirth", False, "feeling", "prefontal cortex", 5),
    ("fear", False, "feeling", "prefontal cortex", 0),
    ("croissant", True, "food", "france", 4),
]

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

Now, even the name of the file will change over time with the system it's testing. And––even better––the naming convention of these test modules is saved from fickle human arbitrariness. 💪🏽
