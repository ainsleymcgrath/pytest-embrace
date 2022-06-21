import pytest

from .embrace import Embrace
from .exc import EmbraceError
from .loader import from_module, revalidate_dataclass


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
    cases = (
        [
            revalidate_dataclass(case, alias=f"{case.__class__.__name__} #{i + 1}")
            for i, case in enumerate(table)
        ]
        if table is not None
        else [from_module(cls, metafunc.module)]
    )

    metafunc.parametrize("case", cases, ids=[str(c) for c in cases])
