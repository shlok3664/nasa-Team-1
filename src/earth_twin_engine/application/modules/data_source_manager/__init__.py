"""Data Source Manager application module."""

from .data_source_adapter import DataSourceAdapter
from .data_source_errors import (
    AmbiguousDataSourceError,
    DataSourceError,
    DataSourceNotFoundError,
    DataSourceResponseError,
    DataSourceUnavailableError,
    DuplicateDataSourceError,
    NoCompatibleDataSourceError,
)
from .data_source_manager import DataSourceManager
from .data_source_manager_module import DataSourceManagerModule
from .queries import (
    FindCompatibleDataSourcesQuery,
    GetDataSourceQuery,
    ListDataSourcesQuery,
)
from .query_handlers import (
    FindCompatibleDataSourcesHandler,
    GetDataSourceHandler,
    ListDataSourcesHandler,
)

__all__ = [
    "AmbiguousDataSourceError",
    "DataSourceAdapter",
    "DataSourceError",
    "DataSourceManager",
    "DataSourceManagerModule",
    "DataSourceNotFoundError",
    "DataSourceResponseError",
    "DataSourceUnavailableError",
    "DuplicateDataSourceError",
    "FindCompatibleDataSourcesHandler",
    "FindCompatibleDataSourcesQuery",
    "GetDataSourceHandler",
    "GetDataSourceQuery",
    "ListDataSourcesHandler",
    "ListDataSourcesQuery",
    "NoCompatibleDataSourceError",
]
