import pytest
from pyperclip import copy

from .embrace import registry
from .exc import EmbraceError
from .gen import gen_text
from .loader import from_module, from_trickling_module


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    registry_ = registry()
    embracers = [name for name in metafunc.fixturenames if name in registry_]

    if len(embracers) > 1:
        raise EmbraceError(f"Can't request multiple Embrace fixtures. Got {embracers}")

    if len(embracers) == 0:
        return

    (sut,) = embracers
    cls = registry_[sut]
    if hasattr(metafunc.module, "table"):
        cases = from_trickling_module(cls, metafunc.module)
    else:
        cases = [from_module(cls, metafunc.module)]

    metafunc.parametrize("case", cases, ids=[str(c) for c in cases])


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--embrace", help="")
    parser.addoption("--embrace-table")
    parser.addoption("--embrace-doc")


def pytest_runtestloop(session: pytest.Session) -> object:
    generate_for = session.config.getoption("--embrace")
    if generate_for is None:
        return None

    registry_ = registry()
    if generate_for not in registry_:
        pytest.exit(
            f"No such fixture '{generate_for}'."
            f" Your options are {sorted([*registry_])}"
        )

    copypasta = gen_text(generate_for)
    print(f"\nCopying the following output to your clipboard:\n{copypasta}")
    copy(copypasta)

    return object()  # stop the loop
