from __future__ import annotations

import traceback
from importlib import reload

import pytest
from pyperclip import copy

from pytest_embrace.codegen import CodeGenManager

from .embrace import registry
from .loader import find_embrace_requester, load


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    sut = find_embrace_requester(metafunc=metafunc, registry=registry())
    if sut is None:
        return
    cases = load(sut)
    metafunc.parametrize("case", cases, ids=[str(c) for c in cases])
    reload(metafunc.module)  # this guarantees the safety of module scope.
    # by reloading at the end of a run, any future references to the just-tested module
    # will encounter it in its 'fresh' state.
    # see ../tests/test_plugin/test_safe_mutable_module_scope.py


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--embrace",
        help=(
            "Takes the name of an Embrace() caller fixture and generates scaffolding"
            " for a new test module that will use it."
            "\nRun `pytest --embrace-ls` to see all the available caller fixtures."
        ),
    )
    parser.addoption(
        "--embrace-ls",
        help="List all the fixtures created for calling Embrace() test suites.",
        action="store_true",
    )
    parser.addoption(
        "--embrace-gen",
        help="Generate code for some fixture:generator",
    )


STOP_LOOP = object()  # for pytest hooks that stop on the first-non-None-result


def pytest_runtestloop(session: pytest.Session) -> object:
    codegen_directive: str | None = session.config.getoption("--embrace")
    do_ls: bool | None = session.config.getoption("--embrace-ls")

    if codegen_directive is None and do_ls is None:
        return None  # allow normal pytest to happen

    reg = registry()

    if codegen_directive is not None:
        codegen = CodeGenManager(codegen_directive, registry=reg)
        if codegen.case_type is None:
            pytest.exit(
                f"No such fixture '{codegen.fixture_name}'."
                f" Your options are {sorted([*reg])}"
            )
        try:
            copypasta = codegen.render()
        except Exception:
            print(f"Error generating {codegen.generator_name}:")
            # TODO print more when -vv given
            traceback.print_exc(limit=0)
            return STOP_LOOP

        print(f"\nCopying the following output to your clipboard:\n\n{copypasta}")
        copy(copypasta)
        return STOP_LOOP

    if do_ls is True:
        print()
        print(f"The following {len(reg)} Embrace() fixtures are abailable:\n")
        print("\n".join(f"{name}  (via {cls.type_name})" for name, cls in reg.items()))

        return STOP_LOOP

    return None
