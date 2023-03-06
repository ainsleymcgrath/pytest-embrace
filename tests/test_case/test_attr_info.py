# skip the future import because it breaks dataclass.fields()
# and turns each Field.type to a string!
# isort: dont-add-import: from __future__ import annotations


import sys
from collections import ChainMap
from dataclasses import dataclass, fields
from typing import Callable, Mapping, Union

from pytest_embrace.case import AttrInfo
from pytest_embrace.codegen import AttrRender


@dataclass
class XYZ:
    one: int
    two: Callable[[Union[ChainMap, int]], Mapping[str, int]]


_fields_lookup = {f.name: f for f in fields(XYZ)}


def test_render_import_statement_global() -> None:
    """Expect no import."""
    attr = _fields_lookup["one"]
    info = AttrInfo(attr)
    renderer = AttrRender(info)
    assert renderer.imports() == ""


def test_render_import_statement_builtins_and_third_party() -> None:
    """Expect every import.
    Note on Python < 3.9:
        3.9 and after alias typing.Callable, typing.Mapping, etc
        to collections.abc. So when solving imports the latter is 'correct'
        in newer Pythongs."""
    attr = _fields_lookup["two"]
    info = AttrInfo(attr)
    renderer = AttrRender(info)
    imports = renderer.imports()
    assert (
        imports
        == "\n".join(
            [
                "from collections import ChainMap",
                (
                    "from collections.abc import Callable, Mapping"
                    if sys.version_info >= (3, 9)
                    else "from typing import Callable, Mapping, Union"
                ),
                # Union is absent below 3.9 because it gets isort'd into the above
                "from typing import Union" if sys.version_info >= (3, 9) else "",
            ]
        ).strip()
    )
