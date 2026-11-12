"""Severity levels for scientific data validation issues."""

from enum import Enum


class ValidationSeverity(Enum):
    """Describes the severity of a validation issue."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
