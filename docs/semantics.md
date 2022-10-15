# The Semantics of an Embrace Test

!!! info "Read on only if you find academic stuff interesting."

    This page goes over the broad strokes of how module tests are put together.

    It's a formal-ish walkthrough of the guaranteed behaviors offered by tests that _use_ this framework.

    **If you just want to use the framework, check out [Usage](./usage/index.md) or Reference.**

pytest-embrace does not do a lot of magic.

It simply uses the attributes of a module that Pytest would have picked up anyway to generate tests. This feature is [well-documented](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#fixtures-can-introspect-the-requesting-test-context) but under-loved.

Pytest says _"You can use variables in module scope as a part of your testing mechanism"_ and pytest-embrace responds _"Ok! Let's formalize that."_

## The Formalism

Over the years of experimentation and expansion, this framework has settled into these 6 tenets:

1. Tests have a schema defined by some class.
2. Test schemas are bound to a special Pytest fixture.
3. Modules implement the schema by requesting that fixture and defining free variables.
4. A test module may contain a literal list of the class it implements.
5. Members of the list can inherit certain attributes defined in module scope.
6. The module can inherit certain attributes from the test file name.

Let's break them down with an example.

### 1. Tests have a schema defined by some class.

With the framework, that's just a dataclass.

```python
@dataclass
class FooTestCase:
    given_word: str
    coefficient: int
    expected_word: str
```

The dataclass describes the schema of inputs and expected outputs of some test.

### 2. Test schemas are bound to a special Pytest fixture.

The "binding" is done with the `pytest_embrace.Embrace` class and its `.fixture` decorator.

```python
emb = Embrace(FooTestCase)


@emb.fixture
def foo_case(case: FooTestCase) -> str:
    result = case.given_word * case.coefficient
    assert result == case.expected_word
    return result
```

The fixture uses the attributes of a `FooTestCase` to run a test.

### 3. Modules implement the schema by requesting that fixture and defining free variables.

A fixture "request" in [Pytest parlance](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#requesting-fixtures) is just a reference to its name in a test function signature.

```python
# test_something.py
def test(foo_case: CaseArtifact[FooTestCase]):
    ...
```

Since `foo_case` makes assertions and whatnot, the test doesn't strictly need a body.

!!! note "Take note of the `CaseArtifact`"

    The framework wraps the return value of your test and the case instance in this object. This enables introspection in the body of `test` and leaves room for us to add extra goodies in the future.

To finish the implementation, define the required attributes of your case as module-scoped variables.

```python
# test_something.py
given_word = "hi"
coefficient = 2
expected_word = "hihi"


def test(foo_case: CaseArtifact[FooTestCase]):
    ...
```

!!! success "This is as far as you need to go to implement a test module."

    After this, we'll be looking at relatively-more-advanced (and very useful) features.

### 4. A test module may contain a literal list of the class it implements.

The reason you'd do this is to run many [parametrized](https://docs.pytest.org/en/7.1.x/how-to/parametrize.html#how-to-parametrize-fixtures-and-test-functions) tests from your module.

In embrace parlance, that would (by default) be a variable named `table` that is an instance of `list[FooTestCase]`.

```python
# test_something.py
table = [
    FooTestCase(
        given_word="hi",
        coefficient=2,
        expected_word="hihi",
    ),
    FooTestCase(
        given_word="hi",
        coefficient=3,
        expected_word="hihihi",
    ),
]


def test(foo_case: CaseArtifact[FooTestCase]):
    ...
```

`test_something.py` has gone from 1 passing test to 2.

### 5. Members of the list can inherit certain attributes defined in module scope.

This expands on tenet #4. `table` is useful for grouping related functionality, but can introduce repetition.

In the above example, `given_word = "hi"` in both test cases. It would be preferable to declare that value only once, sill all tests in `table` use it.

To create this behavior, use the `trickles()` [field specifier](https://docs.python.org/3/library/dataclasses.html#dataclasses.field) on the schema class.

```python
@dataclass
class FooTestCase:
    given_word: str = trickles()
    coefficient: int
    expected_word: str
```

The above change causes a declaration of `given_word` in module scope to "trickle down" into members of `table` that do not specify a value for it themselves. The test file can now be written this way:

```python
# test_something.py
given_word="hi"

table = [
    FooTestCase(
        coefficient=2,
        expected_word="hihi",
    ),
    FooTestCase(
        coefficient=3,
        expected_word="hihihi",
    ),
]


def test(foo_case: CaseArtifact[FooTestCase]):
    ...
```

If a test is added that needs a different value for `given_word`, it can be passed as normal to "override" the default.

```python
# test_something.py
given_word="hi"

table = [
	# omitted for brevity...
    FooTestCase(
        given_word="yo"
        coefficient=5,
        expected_word="yoyoyoyoyo",
    ),
]


def test(foo_case: CaseArtifact[FooTestCase]):
    ...
```

Overriding can be disallowed by passing `no_override=True` to `trickles`.

### 6. The module can inherit certain attributes from the test file name.

Naming many test modules can be difficult, as arbitrary names can drift from the intent of the test.

In order to address this, a schema can extract substrings from a test file's name.

This is accomplished by using the `derive_from_filename()` [field specifier](https://docs.python.org/3/library/dataclasses.html#dataclasses.field).

```python
@dataclass
class FooTestCase:
    given_word: str = derive_from_filename()
    coefficient: int
    expected_word: str
```

By default, this extracts everything after `test_` in the name of a file.

If the name of `test_something` was changed to `test_hi`, then the module-scoped value of `given_word` can be omitted.

```python
# test_hi.py
table = [
    FooTestCase(
        coefficient=2,
        expected_word="hihi",
    ),
    FooTestCase(
        coefficient=3,
        expected_word="hihihi",
    ),
]


def test(foo_case: CaseArtifact[FooTestCase]):
    ...
```

Unlike `trickles()`, the value of a `derive_from_filename()` field can not be overridden.

However, you're not limited to strings. The `parse` keyword arg for `derive_from_filename` takes a `Callable[[str], Any]` that receives the substring. The substring can be used to, for example, call `getattr` on some module or create an instance of some object using the string.

## In short

"Module tests" are not a formal thing.

They really ought to be, because:

- _"Flat is better than nested_ and _"Namespaces are a honking great idea"_ as they say in the Python manifesto
- Markup-like tests (with minimal logic) are easy to read, think about, and ––most importantly–– generate.
- Pytest already made the tool, so let's use it!
- Testing this way has made a big difference at my work.

Try `pytest-embrace` and let me know what you think! I think you'll like it. 😄
