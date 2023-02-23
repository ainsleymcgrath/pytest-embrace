from __future__ import annotations

from importlib import reload

import pytest
from pyperclip import copy

from .embrace import ParsedGeneratorInput, registry
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
    generate_for: str | None = session.config.getoption("--embrace")
    do_ls: bool | None = session.config.getoption("--embrace-ls")
    custom_generator: str | None = session.config.getoption("--embrace-gen")

    if generate_for is None and do_ls is None:
        return None  # allow normal pytest to happen

    reg = registry()

    if generate_for is not None:
        case_type = reg.get(generate_for)
        if case_type is None:
            pytest.exit(
                f"No such fixture '{generate_for}'."
                f" Your options are {sorted([*reg])}"
            )

        # XXX inj here
        copypasta = case_type.render_skeleton()
        print(f"\nCopying the following output to your clipboard:\n{copypasta}")
        copy(copypasta)
        return STOP_LOOP

    if custom_generator is not None:
        user_input = ParsedGeneratorInput(custom_generator)
        case_type = reg.get(user_input.fixture_name)
        if case_type is None:
            pytest.exit(
                f"No such fixture '{user_input.fixture_name}'."
                f" Your options are {sorted([*reg])}"
            )
        generator = case_type.generators[user_input.generator_name]
        case = generator(**user_input.kwargs)
        copypasta = case_type.render_with_values_from(case)
        print(f"\nCopying the following output to your clipboard:\n{copypasta}")
        copy(copypasta)
        return STOP_LOOP

    if do_ls is True:
        print()
        print(f"The following {len(reg)} Embrace() fixtures are abailable:\n")
        print("\n".join(f"{name}  (via {cls.type_name})" for name, cls in reg.items()))

        return STOP_LOOP

    return None
