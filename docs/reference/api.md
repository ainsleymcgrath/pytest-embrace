# API Reference

Find information here about the `pytest_embrace` module and its tools for [designing](#designing-cases), [running](#running-tests), and [writing](#writing-tests) tests.

## Designing Cases

All of these are exposed in `pytest_embrace`. Use them in your case `dataclass`.

### `trickles()`

Marks an attribute as one that can 'trickle down' from module scope into table cases as a default value.

- Mirrors the signature of [`dataclasses.field`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field) and is used in the same way.
- Adds 1 extra optional keyword-only argument: `no_override: bool` (default: `False`)
  - With `no_override = True`, members of `table` can't override the module-level value of that attribute.

### `derive_from_filename()`

Marks an attribute as derived from the name of an enclosing test file.

- Unlike `trickles()`, can't be oeverridden.
  - Similar to trickles, all members of `table` inherit the value derived from the filename.
- Adds 2 extra optional keyword-only arguments
  - `pattern: str` (default: `[\w\.]*test_([\w].*)`)
    - This is used to extract a substring from a test filename.
    - **Note:** The `.py` extension is not looked at.
    - Default extraction is everything after the `test_` prefix.
  - `parse: Callable[[str], Any]` (default: `lambda s: s`)
    - `parse` leverages the extracted substring to define anything you want.
    - A example would be `parse = lambda s: getattr(some_module, s)`

## Running Tests

All of these are exposed in `pytest_embrace`. Use them to create a fixture to run your tests and inspect their results.

### `Embrace`

The entrypoint for creating test cases from a dataclass.

Register a dataclass as a module test schema and create a configurator for defining how tests that implement it will run.

### `Embrace.fixture()`

Create the fixture that will handle the logic of running cases based on the class `Embrace` was instantiated with.

- Must take an argument called `case` that is type-hinted as `YourCaseType`.
- Otherwise behaves just like a normal Pytest fixture.

### `CaseArtifact `

Wraps the instance of a case used for a test run along with whatever was returned by the case fixture.

Allows for one-off introspection and debugging in tests.

- Exposes 2 properties:
  - `case`, the actual instance of your case object created during the test run
  - `actual_result`, the return value of the fixture.

## Writing Tests

These aren't tools from the `pytest_embrace` module, but rather usage patterns.

### `table`

When `pytest-embrace` sees a variable named `table` in a test file **and** that variable is an instance of `list[YourCaseType]`, the test is then [parametrized](https://docs.pytest.org/en/7.1.x/how-to/parametrize.html?highlight=parametrize) with that list.

If you declare a variable named `table` that is not an instance of `list[YourCaseType]`, it is treated normally.

!!! info

    Right now, there is no explicit way to force a variable to be treated as `table`. Implementing such a feature is a high priority and should happen soon.

### `typing.Annotated`

This is mostly a fun easter egg :)

!!! warning

    This is available only in Python 3.9+

When a variable in a case dataclass is type hinted with `Annotated` and the second argument to `Annotated` is a string, that string is injected as a comment in rendered copypasta tests.

```python
class MyCase:
	foo: Annotated[tuple, "Foo is a foo!"]

emb = Embrace(MyCase)

@emb.fixture
def my_case(case: MyCase): ...
```

Later, when generating a `my_case` test, a comment will appear in the generated output.

```python
# some_test.py

foo: str  # Foo is a foo!

def test(my_case): ...
```
