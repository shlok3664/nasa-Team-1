"""Query for listing registered data sources."""

from dataclasses import dataclass

from earth_twin_engine.application.queries import ApplicationQuery


@dataclass(frozen=True, slots=True)
class ListDataSourcesQuery(ApplicationQuery):
    pass
