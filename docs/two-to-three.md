# Handling the API Change

!!! warning "3.0 is not backwards compatible at all"

    The `register_case_runner` and `caller_fixture_factory` methods will raise exceptions that prompt you to migrate. In future releases, they will be removed completely.

## Background

In `pytest-embrace<=3.0`, module test fixtures were created in two steps.

```python
@dataclass
class MyCase:
    attr: str


emb = Embrace(MyCase1)

# STEP 1 -> Create a 'runner'
@emb.register_case_runner
def runner(case: MyCase1, fix: str) -> None:
    pass


# STEP 2 -> Create a 'caller'
my_case = emb.caller_fixture_factory("my_case")
```

`runner` and `caller` represented two distinct fixtures.

**Continued development and usage of the framework has revealed that this distinction is totally useless. ** It's boilerplate and we _hate_ boilerplate.

In versions 3.0 and above, the `Embrace` class has a method called `fixture` that combines the two previous methods.

```python
@dataclass
class MyCase:
    attr: str


emb = Embrace(MyCase1)


@emb.fixture
def my_case(case: MyCase1, fix: str) -> None:
    pass
```

This is more idiomatic with how Pytest usually works and gets rid of the confusing extra moving part of a "caller fixture."

## Migrating

It's easy!

1. Delete the fixture defined with `caller_fixture_factory`
2. Change the name of the function decorated with `register_case_runner` to the name formerly assigned to the result of `caller_fixture_factory`
3. Change `register_case_runner` to `fixture`

All done! 🎉
