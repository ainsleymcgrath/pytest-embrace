class EmbraceError(Exception):
    """Base for framework errors."""


class CaseConfigurationError(EmbraceError):
    """Raise at build/collection time."""
