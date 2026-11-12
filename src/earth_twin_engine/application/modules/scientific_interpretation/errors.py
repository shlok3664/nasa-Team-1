"""Errors raised by the scientific interpretation module."""


class ScientificInterpretationError(Exception):
    """Base exception for scientific interpretation errors."""


class ScientificInterpretationDataError(ScientificInterpretationError):
    """Raised when an interpretation cannot be derived from available data."""

