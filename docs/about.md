# About

Pytest Embrace is a formalism born from patterns used at [Amper](https://www.amper.xyz/) to bring functional tests to old, under-tested, complex backend applications in a way that would still be Nice for newer repos to build their foundation on.

## Philosophy 💡

1. [Table-oriented](https://dave.cheney.net/2019/05/07/prefer-table-driven-tests) ([parametrized](https://docs.pytest.org/en/6.2.x/parametrize.html)) tests are indespensible.

2. Type hints and modern Python [dataclasses](https://docs.python.org/3/library/dataclasses.html) are very good.

3. As sayeth the [Zen](https://peps.python.org/pep-0020/):

   ```
   Flat is better than nested.
   Sparse is better than dense.
   ...
   There should be one-- and preferably only one --obvious way to do it.
   ...
   Namespaces are one honking great idea -- let's do more of those!
   ```

4. Code generation is *really* [underrated](https://github.com/copier-org/copier/).

5. The wave of [type-driven](https://pydantic-docs.helpmanual.io/) [Python](https://github.com/beartype/beartype) [tools](https://typer.tiangolo.com/) [is](https://peps.python.org/pep-0593/) [very](https://github.com/python/mypy) cowabunga––and only just beginning 💡
