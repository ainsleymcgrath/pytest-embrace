from __future__ import annotations


class EmbraceError(Exception):
    """Base for framework errors."""


class CaseConfigurationError(EmbraceError):
    """Raise at build/collection time."""


class CodeGenError(EmbraceError):
    """Raise when anything related to codegen goes awry."""
