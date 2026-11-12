"""Errors raised by regional comparison operations."""


class RegionalComparisonError(Exception):
    """Base exception for regional comparison."""


class InvalidRegionalComparisonError(RegionalComparisonError, ValueError):
    """Raised when a comparison request is invalid."""


class RegionalComparisonDataError(RegionalComparisonError):
    """Raised when regions do not have suitable comparison data."""


class RegionNotFoundForComparisonError(RegionalComparisonError):
    """Raised when a requested region is not registered."""
