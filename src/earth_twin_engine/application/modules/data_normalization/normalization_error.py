"""Errors raised during scientific data normalization."""


class NormalizationError(Exception):
    """Base exception for data normalization failures."""


class UnsupportedUnitConversionError(NormalizationError):
    """Raised when no explicit conversion exists between two units."""


class VariableMismatchError(NormalizationError):
    """Raised when a time series does not represent the requested variable."""
