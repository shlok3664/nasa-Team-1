"""Query handlers for Earth variable discovery."""

from earth_twin_engine.application.modules.variable_discovery.queries import (
    DiscoverEarthVariablesQuery,
    GetEarthVariableQuery,
)
from earth_twin_engine.application.modules.variable_discovery.variable_catalog import (
    VariableCatalog,
)
from earth_twin_engine.domain.variables.earth_variable import EarthVariable


class GetEarthVariableHandler:
    """Handles individual Earth variable lookup."""

    def __init__(self, catalog: VariableCatalog) -> None:
        if not isinstance(catalog, VariableCatalog):
            raise TypeError("catalog must be a VariableCatalog")

        self._catalog = catalog

    def handle(self, query: GetEarthVariableQuery) -> EarthVariable:
        if not isinstance(query, GetEarthVariableQuery):
            raise TypeError("query must be a GetEarthVariableQuery")

        return self._catalog.get(query.variable_id)


class DiscoverEarthVariablesHandler:
    """Handles filtered Earth variable discovery."""

    def __init__(self, catalog: VariableCatalog) -> None:
        if not isinstance(catalog, VariableCatalog):
            raise TypeError("catalog must be a VariableCatalog")

        self._catalog = catalog

    def handle(
        self,
        query: DiscoverEarthVariablesQuery,
    ) -> tuple[EarthVariable, ...]:
        if not isinstance(query, DiscoverEarthVariablesQuery):
            raise TypeError("query must be a DiscoverEarthVariablesQuery")

        return self._catalog.discover(
            category=query.category,
            keyword=query.keyword,
            temporal_resolution=query.temporal_resolution,
            source_id=query.source_id,
        )
