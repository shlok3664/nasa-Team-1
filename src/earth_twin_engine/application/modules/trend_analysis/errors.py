"""Errors raised by trend analysis operations."""


class TrendAnalysisError(Exception):
    """Base exception for trend analysis."""


class TrendSeriesNotFoundError(TrendAnalysisError):
    """Raised when the requested time series does not exist."""


class InsufficientTrendDataError(TrendAnalysisError):
    """Raised when a trend cannot be calculated from the supplied data."""


class InvalidTrendConfigurationError(TrendAnalysisError, ValueError):
    """Raised when trend analysis configuration is invalid."""
