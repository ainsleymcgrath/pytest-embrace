# Noble Copypasta

Unit tests are the most tragic victim of haphazard copypasta.

_And_ they are a totally understandable thing to copy-paste.

But it's fine until its not. Docstrings go stale, filenames make no sense, random unrelated state gets set up during tests, suites are repeated. Sadness ensues.

That said, `Cmd + V` is _very_ few keystrokes to get a new test case going. And that's appealing. So this plugin makes copypasta a first-class-feature!

## `pytest` Options

`pytest-embrace` adds 2 extra options to the `pytest` command.

1. `--embrace-ls` will list out any _caller fixtures_ that have been created in your codebase.
2. `--embrace <fixture name>` will print the scaffolding of a new test module to the console, and copy it to your clipboard. Check out an example in the [Making Cases](../designing-tests/making-cases#code-generation) documentation.

## Comments via `Annotated`

!!! warning "Limited use feature"
    Since this feature uses `typing.Annotated`, Python versions <=3.8 do not support it.

`Embrace()` test suites are complicated. Sometimes it may be difficult to grok the purpose of all the variables that show up in a generated module. So `pytest-embrace` provides a mechanisms for adding comments via [Pep 593](https://peps.python.org/pep-0593/) annotations.

!!! info
    `Annotated[]` is a type-hint that takes the type you're hinting as its first arg, and then arbitrary stuff after. Like `Annotated[int, Whatever(), "Anything works!"]` counts as an `int`, but Library authors (me) can use those extra arguments to implement special behaviors.

To add a comment to generated code, simply pass a string to `Annotated`:

```python title="conftest.py"
@dataclass
class CommentedCase:
    confusing_attribute: Annotated[
        object, "This one is confusing. I have no further help for you :("
    ]


comment_case_config = Embrace(CommentedCase)


@comment_case_config.register_case_runner
def run_comment_case(case: CommentedCase) -> None:
    pass


comment_case = comment_case_config.caller_fixture_factory("comment_case")
```

When you generate code for `comment_case`...

```shell
$ pytest --embrace comment_case
```

you get this:

```python
from pytest_embrace import CaseArtifact

from conftest import CommentedCase


confusing_attribute: object  # This one is confusing. I have no further help for you :(


def test(comment_case: CaseArtifact[CommentedCase]) -> None:
    ...
```
