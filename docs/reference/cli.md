# CLI Reference

Find information about the command-line options exposed in `pytest` by `pytest-embrace`.

## Pytest Options

All of these are added to the `pytest` executable when `pytest-embrace` is installed.

### `--embrace-ls`

List all fixtures registered with `Embrace` along with their case objects.

### `--embrace <fixture_name>`

Generate a skeleton test module and send it to your clipboard.

### `--embrace <fixture_name>:<generator_name> [<arg>=<value> ...]`

Runs the `Embrace.generator` decorated function named `<generator_name>` with the given`arg=value` pairs as keyword arguments.

Given this:

```python
e = Embrace(SomeCase)

@e.fixture
def fix(): ...

@e.generator
def gen(arg): ...
```

You can call this:

```shell
pytest --embrace 'fix:gen arg=something'
```
