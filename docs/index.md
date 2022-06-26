# Pytest Embrace

![Image title](logotype.svg)

> _Reject boilerplate. Embrace complexity._

## What is this?

`pytest-embrace` is a Pytest-plugin-cum-metaframework that facilitates structured, iterative, type-driven unit testing.

It is the formalization of the approach we've adopted for end-to-end testing of complex backend services at [Amper](https://www.amper.xyz).

## Why should I use it?

Because you like unit testing with Pytest, you like types, you're lazy-and-intrepid, and you're willing to trust me. 😄

If you know how to use dataclasses and Pytest fixtures, getting started requires very little knowledge beyond that.

## When should I use it?

The pattern employed by `pytest-embrace` could technically be applied to any unit tests.

In practice, however, it does best when:

- You have enormously tall [parametrized](https://docs.pytest.org/en/7.1.x/how-to/parametrize.html#parametrize) tests that have become hard to grok and maintain.
- You are testing a consistent interface at a high level (think API endpoints) that rely on external state (like databases).
  - And you've realized over time that all those tests are _pretty much_ the same... but nuance makes parametrizing hard and you resign yourself to long breadcrumb trails of fixtures that may-or-may-not actually be used by your tests and just like... 😤 ugh.
- You like type safety, generating code, iterating quickly, testing exhaustively, and being DRY.

## How does it work?

Let's break it down. The following is pseudocode to capture the spirit of what I write at work. In real life, it would live in a `conftest.py` file.

For runnable, more deeply-explained, and feature-filled examples, see the [Usage Guide](./usage-guide.md).

> ℹ️ _The following is not beginner Python code._ > _Decent knowledge of Pytest and type-hints are required to use `pytest-embrace`._

**First, define a dataclass** that describes the system under test, requisite state, expected outputs, expected mutations, etc.

```javascript
const { foo, bar } = func(() => {})
```



```python
@dataclass
class RestApiCase:
    verb: Literal['get', 'put', 'post', 'patch', 'delete']
    endpoint: str
    request_body: dict | None
    expected_response: dict | None

    seed_tables: dict[str, Path]  # mapping of table names to CSVs
    sql_after: list[tuple[str, str]]  # some queries + their expected results
```

**Next, import `Embrace` from the library and feed it your class.**

```python
from pytest_embrace import Embrace

e = Embrace(RestApiCase)
```

**Now, register a test _runner_ fixture**––which is just a slightly-tweaked Pytest fixture. It **must** be typed and it **must** include your case object. It can include **any** other fixtures you've defined.

It'll end up looking like a familiar Pytest test suite.

```python
@e.register_case_runner
def run_rest_api_test(
    case: RestApiCase, testdb: Database, testclient: ApiClient
) -> dict[str, list | dict | None]:
    for table, csv in case.seed_tables.items():
        testdb.insert_csv(table, csv)

	requester_func = getattr(testclient, case.verb)
    response = requester_func(case.endpoint, data=case.request_body)
    assert case.expected_response == response

    got_db_records: list[Any] = []
    for query, expected_result in case.sql_after:
        result = testdb.execute(case.query)
        got_db_records += [result]
        assert result == expected_result


    return {"got_db_records": got_db_records, "actual_response": response}
```

This is the weird part: **Define a _caller_ fixture** using the `Embrace` instance. This is what you'll request in test cases to automagically run your test and generate new cases.

```python
rest_api_case = e.caller_fixture_factory('rest_api_case')
```

> _👆🏽 What the heck?? Without getting too far into it, `caller_fixture_factory` returns a Pytest fixture. Pytest needs to be able to see it in module-scope in your conftest, and `pytest-embrace` needs to know the name of the the fixture, too. This form is fairly common. Think `MyObject = NamedTuple('MyObject', ...)` or `T =TypeVar('T')`._

Now you can **generate a test scaffold** using the name of the caller fixture.

```shell
# we're in the shell now
pytest --embrace rest_api_case
```

The following code will arrive in your clipboard:

```python
from pytest_embrace import CaseArtifact

from conftest import RestApiCase

verb: Literal['get', 'put', 'post', 'patch', 'delete']
endpoint: str
request_body: dict | None
expected_response: dict | None

seed_tables: dict[str, Path]
sql_after: list[tuple[str, str]]


def test(rest_api_case: CaseArtifact[RestApiCase]) -> None:
    ...
```

> ℹ️ _`CaseArtifact` has an `actual_result` attribute that contains the return value of your runner fixture and a `case` attribute that contains the instance of `RestApiCase` used._
>
> _Here, for example, you could get after `rest_api_case.actual_result['got_db_records']`_.

🎉 **Congratulations!** 🎉 You may now declare your test with the comfort of autocompletion and a fantastically high signal-noise-ratio. And you can do it over and over with the clipboard you love so much.

For more examples that you copy, paste, and run youreslf see [Usage](./usage.md)
