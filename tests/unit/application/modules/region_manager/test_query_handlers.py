import pytest

from earth_twin_engine.application.modules.region_manager import (
    FindRegionsContainingHandler,
    FindRegionsContainingQuery,
    GetGeographicRegionHandler,
    GetGeographicRegionQuery,
    ListGeographicRegionsHandler,
    ListGeographicRegionsQuery,
    RegionManager,
    RegionNotFoundError,
)
from earth_twin_engine.domain.geography import (
    GeographicRegion,
    SpatialCoordinate,
)


def test_get_geographic_region_handler(
    india_region: GeographicRegion,
) -> None:
    manager = RegionManager()
    manager.register(india_region)

    handler = GetGeographicRegionHandler(manager)
    result = handler.handle(GetGeographicRegionQuery(region_id="india"))

    assert result is india_region


def test_get_geographic_region_handler_rejects_missing_region() -> None:
    handler = GetGeographicRegionHandler(RegionManager())

    with pytest.raises(RegionNotFoundError, match="india"):
        handler.handle(GetGeographicRegionQuery(region_id="india"))


def test_get_geographic_region_handler_rejects_invalid_query() -> None:
    handler = GetGeographicRegionHandler(RegionManager())

    with pytest.raises(TypeError, match="GetGeographicRegionQuery"):
        handler.handle(ListGeographicRegionsQuery())  # type: ignore[arg-type]


def test_list_geographic_regions_handler(
    india_region: GeographicRegion,
    japan_region: GeographicRegion,
) -> None:
    manager = RegionManager()
    manager.register(japan_region)
    manager.register(india_region)

    handler = ListGeographicRegionsHandler(manager)
    result = handler.handle(ListGeographicRegionsQuery())

    assert result == (india_region, japan_region)


def test_list_geographic_regions_handler_returns_empty_tuple() -> None:
    handler = ListGeographicRegionsHandler(RegionManager())

    result = handler.handle(ListGeographicRegionsQuery())

    assert result == ()


def test_list_geographic_regions_handler_rejects_invalid_query() -> None:
    handler = ListGeographicRegionsHandler(RegionManager())

    with pytest.raises(TypeError, match="ListGeographicRegionsQuery"):
        handler.handle(GetGeographicRegionQuery(region_id="india"))  # type: ignore[arg-type]


def test_find_regions_containing_handler(
    india_region: GeographicRegion,
    maharashtra_region: GeographicRegion,
    nagpur_coordinate: SpatialCoordinate,
) -> None:
    manager = RegionManager()
    manager.register(india_region)
    manager.register(maharashtra_region)

    handler = FindRegionsContainingHandler(manager)
    result = handler.handle(FindRegionsContainingQuery(coordinate=nagpur_coordinate))

    assert result == (india_region, maharashtra_region)


def test_find_regions_containing_handler_returns_empty_tuple(
    japan_region: GeographicRegion,
    nagpur_coordinate: SpatialCoordinate,
) -> None:
    manager = RegionManager()
    manager.register(japan_region)

    handler = FindRegionsContainingHandler(manager)
    result = handler.handle(FindRegionsContainingQuery(coordinate=nagpur_coordinate))

    assert result == ()


def test_find_regions_containing_handler_rejects_invalid_query(
    nagpur_coordinate: SpatialCoordinate,
) -> None:
    handler = FindRegionsContainingHandler(RegionManager())

    with pytest.raises(TypeError, match="FindRegionsContainingQuery"):
        handler.handle(GetGeographicRegionQuery(region_id="india"))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "manager",
    [
        None,
        object(),
    ],
)
def test_handlers_reject_invalid_manager(manager: object) -> None:
    with pytest.raises(TypeError, match="RegionManager"):
        GetGeographicRegionHandler(manager)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="RegionManager"):
        ListGeographicRegionsHandler(manager)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="RegionManager"):
        FindRegionsContainingHandler(manager)  # type: ignore[arg-type]
