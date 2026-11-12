"""Errors raised by the Data Source Manager."""


class DataSourceError(Exception):
    """Base exception for data source management failures."""


class DuplicateDataSourceError(DataSourceError):
    """Raised when a source ID is already registered."""


class DataSourceNotFoundError(DataSourceError):
    """Raised when a requested source is not registered."""


class NoCompatibleDataSourceError(DataSourceError):
    """Raised when no registered source supports a request."""


class AmbiguousDataSourceError(DataSourceError):
    """Raised when a request matches multiple sources."""


class DataSourceUnavailableError(DataSourceError):
    """Raised when a selected provider is unavailable."""


class DataSourceResponseError(DataSourceError):
    """Raised when an adapter returns an invalid or inconsistent dataset."""
