"""Errors raised by time-series management operations."""


class TimeSeriesManagementError(Exception):
    """Base exception for time-series management."""


class DuplicateTimeSeriesError(TimeSeriesManagementError):
    """Raised when a series identifier is already registered."""


class TimeSeriesNotFoundError(TimeSeriesManagementError):
    """Raised when a requested series does not exist."""


class IncompatibleTimeSeriesError(TimeSeriesManagementError):
    """Raised when series cannot be combined."""


class TimeSeriesAggregationError(TimeSeriesManagementError):
    """Raised when an aggregation operation fails."""
