"""Supported application logging levels."""

from enum import IntEnum


class LogLevel(IntEnum):
    """Severity levels supported by the application logger."""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
