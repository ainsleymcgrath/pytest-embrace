from collections import ChainMap
from dataclasses import dataclass, fields
from typing import Callable, Mapping, Union

from pytest_embrace.case import AttrInfo


@dataclass
class XYZ:
    one: int
    two: Callable[[Union[ChainMap, int]], Mapping[str, int]]


_fields_lookup = {f.name: f for f in fields(XYZ)}


def test_render_import_statement_global() -> None:
    """Expect no import."""
    attr = _fields_lookup["one"]
    info = AttrInfo(attr)
    assert info.render_import_statement() == ""


def test_render_import_statement_builtins_and_third_party() -> None:
    """Expect every import."""
    attr = _fields_lookup["two"]
    info = AttrInfo(attr)
    imports = info.render_import_statement()
    assert imports == "\n".join(
        [
            "from collections import ChainMap",
            "from collections.abc import Callable, Mapping",  # quirky! re: Callable
            "from typing import Union",
        ]
    )
