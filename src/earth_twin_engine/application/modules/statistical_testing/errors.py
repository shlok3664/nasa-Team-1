"""Errors raised by statistical testing operations."""


class StatisticalTestingError(Exception):
    """Base exception for statistical testing."""


class StatisticalTestNotFoundError(StatisticalTestingError):
    """Raised when a requested statistical test is not registered."""


class DuplicateStatisticalTestError(StatisticalTestingError):
    """Raised when a statistical test is registered more than once."""


class InsufficientStatisticalDataError(StatisticalTestingError):
    """Raised when a statistical test cannot use the supplied observations."""


class IncompatibleStatisticalSamplesError(StatisticalTestingError):
    """Raised when samples cannot be compared by the requested test."""


class InvalidStatisticalTestConfigurationError(
    StatisticalTestingError,
    ValueError,
):
    """Raised when statistical test configuration is invalid."""
