from textwrap import dedent


class EmbraceError(Exception):
    """Base for framework errors."""


class CaseConfigurationError(EmbraceError):
    """Raise at build/collection time."""


class TwoStepApiDeprecationError(EmbraceError):
    """Very specific error for methods deprecated after 3.0."""

    def __init__(self, *, deprecated_method: str) -> None:
        msg = f"""
        `{deprecated_method}` is deprecated in favor of `Embrace.fixture`.
        The new API unifies the old two-step process into one.
        and requires very minimal code changes.

        See migration guide in the docs:
            https://ainsleymcgrath.github.io/pytest-embrace/two-to-three/

        In future releases, this method will completely removed."""

        super().__init__(dedent(msg))
