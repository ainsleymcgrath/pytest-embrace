# Introduction

## Complex Tools for Complex Problems

This framework excels when the following things about your tests are true:

- They are fairly repetitive––like tests for a REST api or a database client.
- The behaviors being tested go beyond the scope of pure inputs and outputs.
- There are many contingencies for the behavior of an interface––errors, mutations, calls to other services, etc.

For this reason, the guide for `pytest-embrace` will deal with a [SQLite](https://www.sqlite.org/index.html) database client. It's [built in](https://docs.python.org/3/library/sqlite3.html) to Python, so no extra dependencies are needed to work through examples.

All of this will be revisited later, but as a prelimanry heads up every piece of functionality will interact with this extremely complicated table of things:

```sql
create table things
(
    name text,
    is_bread bool,
    type text,
    origin text,
    rating int
);
```

The client will consist of a single namespace, `crud.py`, full of functions that access and affect the `things` table. Tests will cover the various ways accessing and affecting that table can play out.

## A Quick Note on Namespaces

With `pytest-embrace`, tests are written as Python modules––individual files––rather than as classes or functions.

The structure of those files is determined by the user using dataclasses. The attributes of the class are expected to match up with any module that associates itself with it.

`pytest-embrace` uses `pytest` to glue together _class_ namespaces with _module_ namespaces, resulting in flat, markup-like test cases with an enforced structure and testing logic defined in exactly one place.

!!! info

    In Python, a "namespace" is quite literally a "space," such as a class or module, that affords access to "names", aka variables and attributes.

Usually, _class_ namespaces don't have anything to do with _module_ namespaces. The latter are used almost exclusively to grab a bunch of related functionality at once:

```python
import sys
import numpy as np
```

This is incredibly convenient and nice for _accessing_ functionality via a clean interface. But for developers, Python does not provide any way to enforce the _creation_ of such interfaces. The composition of a Python file's attributes is the wild west.
