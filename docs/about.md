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

4. Code generation is _really_ [underrated](https://github.com/copier-org/copier/).

5. The wave of [type-driven](https://pydantic-docs.helpmanual.io/) [Python](https://github.com/beartype/beartype) [tools](https://typer.tiangolo.com/) [is](https://peps.python.org/pep-0593/) [very](https://github.com/python/mypy) cowabunga––and only just beginning 💡

## Background

Underneath it all, this plugin/framework is a love letter to Pytest's [parametrization](https://docs.pytest.org/en/6.2.x/parametrize.html) feature.

Parametrization is what makes Pytest really great. It works fantastically well for testing interfaces that can be expressed as _`Given <some_input> expect <some_output> because <some_reason>`._ [Given, expected, should](https://ainsleymcgrath.com/pythonic-pytest-part-2-the-parametrization-mantra/).

But eventually, when you're testing at a higher level than simply calling code you've written, that pattern craps out. Tests that rely on live databases are a great example of this. Pytest handles this gracefully, as it's just Python code and you can write whatever you want.

But that, too, becomes a problem: You can write whatever you want. The snare of arbitrariness leaves you with a mess of redundant, inconsistent fixtures floating around. With vanilla pytest fixtures, you're hung out to dry. If you want to get the structure and consistency of parametrized tests back, you're forced to either write a big ball of mud or learning the [hooks](https://docs.pytest.org/en/6.2.x/reference.html?highlight=assertrepr#hooks) API. Which you should at some point! But it's always felt like overkill for one-offs

**The idea with `pytest-embrace` is to create a looser and more nuance-friendly approach to fixtures and tests. while lowering the bar for leveraging more advanced Pytest test-generation features.**
