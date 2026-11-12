"""Query handlers for geographic region management."""

from earth_twin_engine.application.modules.region_manager.queries import (
    FindRegionsContainingQuery,
    GetGeographicRegionQuery,
    ListGeographicRegionsQuery,
)
from earth_twin_engine.application.modules.region_manager.region_manager import (
    RegionManager,
)
from earth_twin_engine.domain.geography import GeographicRegion


class GetGeographicRegionHandler:
    """Retrieves one registered geographic region."""

    def __init__(self, manager: RegionManager) -> None:
        if not isinstance(manager, RegionManager):
            raise TypeError("manager must be a RegionManager")

        self._manager = manager

    def handle(self, query: GetGeographicRegionQuery) -> GeographicRegion:
        if not isinstance(query, GetGeographicRegionQuery):
            raise TypeError("query must be a GetGeographicRegionQuery")

        return self._manager.get_region(query.region_id)


class ListGeographicRegionsHandler:
    """Lists all registered geographic regions."""

    def __init__(self, manager: RegionManager) -> None:
        if not isinstance(manager, RegionManager):
            raise TypeError("manager must be a RegionManager")

        self._manager = manager

    def handle(
        self,
        query: ListGeographicRegionsQuery,
    ) -> tuple[GeographicRegion, ...]:
        if not isinstance(query, ListGeographicRegionsQuery):
            raise TypeError("query must be a ListGeographicRegionsQuery")

        return self._manager.all_regions()


class FindRegionsContainingHandler:
    """Finds geographic regions containing a coordinate."""

    def __init__(self, manager: RegionManager) -> None:
        if not isinstance(manager, RegionManager):
            raise TypeError("manager must be a RegionManager")

        self._manager = manager

    def handle(
        self,
        query: FindRegionsContainingQuery,
    ) -> tuple[GeographicRegion, ...]:
        if not isinstance(query, FindRegionsContainingQuery):
            raise TypeError("query must be a FindRegionsContainingQuery")

        return self._manager.find_containing(query.coordinate)
