# Writing Tests

Pytest embrace is useful when that "state of affairs" goes beyond pure inputs and outputs. Code that relies on external databases is an excellent example.

**So before embarking on the test, we need some code to test.**

## System Under Test: A Database Client

Specifically a SQLite client, as described in the [Intro](./index.md) .

```python title="crud.py"
from sqlite3 import Connection


class NoRecordFoundError(Exception):
    ...


def is_bread(conn: Connection, name: str) -> bool:
    cursor = conn.execute(
        # in sqlite, `?` is used as a placeholder
        "select is_bread from things where name = ?",
        (name,),
    )
    (result,) = cursor.fetchone()

    return result == 1  # sqlite uses 1/0 for True/False
```

This function, which determines whether or not the record with the given `name` is bread or not. When the function is used, it presupposes

1. A live database
2. The existince of a database table called `things` with an `is_bread` column
3. The presence of records in that table

## Setting Up Tests with Normal Fixtures

To test this, we start by making a pytest fixture to create a database and provide a connection to it.

```python title="conftest.py"
@pytest.fixture
def testconn() -> Iterator[Connection]:
    connection = connect(":memory:")
    connection.execute(
        """
        create table things
        (
            name text,
            is_bread bool,
            type text,
            origin text,
            rating int
        );"""
    )

    yield connection

    connection.execute("drop table things")
    connection.close()
```

Now, we just need some data in there. Let's use another fixture!

```python title="conftest.py"
from sqlite3 import Connection


@pytest.fixture
def testdata(testconn: Connection):
    records = (
        ("mirth", False, "feeling", "prefontal cortex", 5),
        ("fear", False, "feeling", "prefontal cortex", 0),
        ("croissant", True, "food", "france", 4),
    )

    testdb.executemany("insert into things values (?,?,?,?,?)", [*records])

```

And now we're good to test:

```python title="test_crud.py"
def is_bread_true(testdata, testconn: Connection):
    assert is_bread(testconn, 'mirth') is False, "Mirth is a feeling, not bread."
    assert is_bread(testconn, 'croissant') is True, "A croissant is tasty bread."
```

## Describing The State of Affairs with a Dataclass

In order to run the test, we needed a few things:

1. A database with a table in it. This will apply to _all_ the tests.
2. Some known records to seed the DB and query against. This is unique to _this_ test.
3. A function we want to test
4. Some args to pass our function.
5. Some expectations for our function, including a assertion messages.

How can this state of affairs be codified into a test case? Let's take a crack at it.

```python title="conftest.py"
from dataclasses import dataclass


@dataclass
class CrudTestCase:
    seed_data: list[tuple]
    crud_func: Callable[..., Any]
    args: tuple[Any, ...]
    assert_return: Any
    should: str  # assertion message
```

Awesome. Now how will we run it?

## Configuring the Test Run with `Embrace()`

First, we need `Embrace`, and a runner.

```python title="conftest.py"
from sqlite3 import Connection

from pytest_embrace import Embrace

crud_case_config = Embrace(CrudTestCase)

@crud_case_config.fixture
def crud_case_runner(): ...
```

Passing a dataclass to `Embrace` gives us an object instance we can use to configure test cases based on the state of affairs we described.

The `.register_case_runner` function ultimately creates a Pytest fixture, so we have access to any fixtures we've already defined.

Additionally, it _must_ receive an instance of the class you registered and all of its arguments _must_ be typed.

Our first pre-req for testing `is_bread` was an existing database. We already have a fixture for that: `testdb`. So we can just reference it!

```python title="conftest.py"
from sqlite3 import Connection


@crud_case_config.fixture
def crud_case_runner(case: CrudTestCase, testdb: Connection):
    ...
```

The `CrudTestCase` object has that `seed_data` attribute. Let's recycle some code from `testdata` (which we will no longer use, since it hardcoded data and each test will need to define its own).

```python title="conftest.py"
@crud_case_config.fixture
def crud_case_runner(case: CrudTestCase, testconn: Connection) -> object:
    testconn.executemany("insert into things values (?,?,?,?,?)", [*case.seed_data])
```

And now we can put in a more generalized call to the function.

```python title="conftest.py"
@crud_case_config.fixture
def crud_case_runner(case: CrudTestCase, testconn: Connection) -> object:
    testconn.executemany("insert into things values (?,?,?,?,?)", [*case.seed_data])
    result = case.crud_func(*case.args)
    assert case.assert_return == result, case.should
    return result  # (1)
```

1. Take note of the return: It's the actual result of our function call. That'll come back into play later.

## Implement The test

We now have all we need to start writing tests.

### Code Generation

`pytest-embrace` is as much about strict case composition as it is about code generation. So now that we have `crud_case` floating around, let's reference it at the command line:

```shell
pytest --embrace crud_case
```

You'll see this output:

```shell
============================= test session starts ==============================
platform darwin -- Python 3.10.4, pytest-7.1.2, pluggy-1.0.0
rootdir: /Users/ains/repos/pytest-embrace
plugins: embrace-1.0.1
collected 21 items

Copying the following output to your clipboard:

from pytest_embrace import CaseArtifact

from conftest import CrudCase


seed_data: list[tuple]
crud_func: typing.Callable[..., typing.Any]
args: tuple[typing.Any, ...]
assert_return: typing.Any
should: str


def test(crud_case: CaseArtifact[CrudTestCase]) -> None:
    ...
```

The content of the test is in your clipboard, so go ahead and paste it in a new file.

```shell
# for mac users...
pbpaste > test_is_bread_false.py
```

The contents aren't perfect. Not all imports are solved (for now), but it's a strong start!

Let's fill in the blanks, removing type hints as we go. What was formerly expressed as this:

```python
def is_bread_true(testdata, testconn: Connection):
    assert is_bread('mirth') is False, "Mirth is a feeling, not bread."
```

Is now this:

```python title="test_is_bread_false.py"
from pytest_embrace import CaseArtifact

from conftest import CrudCase
from crud import is_bread


seed_data = (
    ("mirth", False, "feeling", "prefontal cortex", 5),
    ("fear", False, "feeling", "prefontal cortex", 0),
    ("croissant", True, "food", "france", 4),
)
crud_func = is_bread
args = ("mirth",)
assert_return = False
should = "Mirth is a feeling, not bread."


def test(crud_case: CaseArtifact[CrudTestCase]) -> None:
    ...
```

### Iterating & Sharing

Now let's do the second test.

```
pytest --embrace crud_case
pbpaste > test_is_bread_true.py
```

Since this test will share a lot of DNA with the first one, it can be configured simply with the import system.

```python title="test_is_bread_true.py"
from pytest_embrace import CaseArtifact

from conftest import CrudTestCase

# shared DNA
from test_is_bread_false import crud_func, seed_data

args = ("croissant",)
assert_return = True
should = "A croissant is tasty bread."


def test(crud_case: CaseArtifact[CrudTestCase]) -> None:
    ...
```

!!! attention

    While using imports this way is a cool trick to share test dependencies, it has proved somewhat controversial/finnicky in practice.

    In the [next section](../tables-and-modules/index.md) and beyond we'll go over some other more structured approaches.

Now we can run these as normal:

```shell
$ pytest
=============================== test session starts ===============================
platform darwin -- Python 3.10.4, pytest-7.1.2, pluggy-1.0.0
rootdir: /Users/ains/repos/pytest-embrace/docs/code-samples
plugins: embrace-0.3.0
collected 2 items

test_is_bread_false.py .                                                    [ 50%]
test_is_bread_true.py .                                                     [100%]

================================ 2 passed in 0.02s ================================
```

### The Artifact

You'll notice very generated test function has this in its singature:

```python
crud_case: CaseArtifact[CrudTestCase]
```

In the event that you want to do anything more after your runner has succeeded, you can access the generated `CrudTestCase` object in its `.case` property, and the return value from the runner in `.actual_result`. Maybe, for example, you want to pull in more fixtures for special-case assertions.

```python title="test_bread_true.py"
...

crud_func = is_bread
args = ("mirth",)
assert_return = False
should = "Mirth is a feeling, not bread."


def test(crud_case: CaseArtifact[CrudTestCase], testconn, caplog) -> None:
    assert "Today's non-bread discovery count is now 1" in caplog.text
    assert crud_case.case.args[0] in caplog.text, "The non-bread is mentioned by name"

    crud_case.case.crud_func(testconn, 'trees')
    assert "Today's non-bread discovery count is now 2" in caplog.text, (
    	"Repeated queries about non-bread increment the counter"
    )
```

This 👆🏽 won't pass because we don't have any logging. It's just to illustrate.
