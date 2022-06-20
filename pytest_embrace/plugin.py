import logging

import pytest

from .embrace import Embrace
from .exc import EmbraceError
from .loader import from_module

logger = logging.getLogger()


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    registry = Embrace._runner_registry
    embracers = [name for name in metafunc.fixturenames if name in registry]

    if len(embracers) > 1:
        raise EmbraceError(f"Can't request multiple Embrace fixtures. Got {embracers}")

    if len(embracers) == 0:
        return

    (sut,) = embracers
    cls = registry[sut]
    table = getattr(metafunc.module, "table", None)
    if table is not None:
        cases = table
    else:
        cases = [from_module(cls, metafunc.module)]

    metafunc.parametrize("case", cases, ids=[str(c) for c in cases])
