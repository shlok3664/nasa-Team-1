"""Severity levels for application errors."""

from enum import IntEnum


class ErrorSeverity(IntEnum):
    """Defines how seriously an application should treat an error."""

    INFO = 10
    WARNING = 20
    ERROR = 30
    CRITICAL = 40
