"""Query handlers for registered data sources."""

from earth_twin_engine.application.modules.data_source_manager.data_source_manager import (
    DataSourceManager,
)
from earth_twin_engine.application.modules.data_source_manager.queries import (
    FindCompatibleDataSourcesQuery,
    GetDataSourceQuery,
    ListDataSourcesQuery,
)
from earth_twin_engine.domain.datasets import DataSource


class GetDataSourceHandler:
    """Retrieves one registered data source."""

    def __init__(self, manager: DataSourceManager) -> None:
        if not isinstance(manager, DataSourceManager):
            raise TypeError("manager must be a DataSourceManager")
        self._manager = manager

    def handle(self, query: GetDataSourceQuery) -> DataSource:
        if not isinstance(query, GetDataSourceQuery):
            raise TypeError("query must be a GetDataSourceQuery")
        return self._manager.get_source(query.source_id)


class ListDataSourcesHandler:
    """Lists all registered data sources."""

    def __init__(self, manager: DataSourceManager) -> None:
        if not isinstance(manager, DataSourceManager):
            raise TypeError("manager must be a DataSourceManager")
        self._manager = manager

    def handle(self, query: ListDataSourcesQuery) -> tuple[DataSource, ...]:
        if not isinstance(query, ListDataSourcesQuery):
            raise TypeError("query must be a ListDataSourcesQuery")
        return self._manager.all_sources()


class FindCompatibleDataSourcesHandler:
    """Finds providers capable of satisfying a data request."""

    def __init__(self, manager: DataSourceManager) -> None:
        if not isinstance(manager, DataSourceManager):
            raise TypeError("manager must be a DataSourceManager")
        self._manager = manager

    def handle(
        self,
        query: FindCompatibleDataSourcesQuery,
    ) -> tuple[DataSource, ...]:
        if not isinstance(query, FindCompatibleDataSourcesQuery):
            raise TypeError("query must be a FindCompatibleDataSourcesQuery")
        return self._manager.find_compatible_sources(query.request)
