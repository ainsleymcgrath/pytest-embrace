from types import ModuleType, SimpleNamespace
from typing import Any, cast


def module_factory(name: str = "module", **kwargs: Any) -> ModuleType:
    return cast(ModuleType, SimpleNamespace(__name__=name, **kwargs))
