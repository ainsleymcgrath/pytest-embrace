import pytest
from pyperclip import copy

from .embrace import Embrace
from .exc import EmbraceError
from .gen import gen_text
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


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--gen")


def pytest_runtestloop(session: pytest.Session) -> object:
    generate_for = session.config.getoption("--gen")
    if generate_for is None:
        return None

    registry = Embrace._runner_registry
    if generate_for not in registry:
        pytest.exit(
            f"No such fixture '{generate_for}'."
            f" Your options are {sorted([*registry])}"
        )

    copypasta = gen_text(generate_for)
    print(f"\nCopying the following output to your clipboard:\n{copypasta}")
    copy(copypasta)

    return object()  # stop the loop
