import pytest

from earth_twin_engine.application.modules.region_manager import (
    FindRegionsContainingQuery,
    GetGeographicRegionQuery,
    ListGeographicRegionsQuery,
)
from earth_twin_engine.domain.geography import SpatialCoordinate


def test_get_geographic_region_query() -> None:
    query = GetGeographicRegionQuery(region_id="india")

    assert query.region_id == "india"
    assert query.query_id is not None
    assert query.issued_at is not None


@pytest.mark.parametrize(
    "region_id",
    [
        "",
        " ",
        None,
        123,
    ],
)
def test_get_geographic_region_query_rejects_invalid_region_id(
    region_id: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        GetGeographicRegionQuery(region_id=region_id)  # type: ignore[arg-type]


def test_list_geographic_regions_query() -> None:
    query = ListGeographicRegionsQuery()

    assert query.query_id is not None
    assert query.issued_at is not None


def test_find_regions_containing_query(
    nagpur_coordinate: SpatialCoordinate,
) -> None:
    query = FindRegionsContainingQuery(coordinate=nagpur_coordinate)

    assert query.coordinate == nagpur_coordinate
    assert query.query_id is not None
    assert query.issued_at is not None


@pytest.mark.parametrize(
    "coordinate",
    [
        None,
        "21.1458, 79.0882",
        (21.1458, 79.0882),
        object(),
    ],
)
def test_find_regions_containing_query_rejects_invalid_coordinate(
    coordinate: object,
) -> None:
    with pytest.raises(TypeError, match="SpatialCoordinate"):
        FindRegionsContainingQuery(coordinate=coordinate)  # type: ignore[arg-type]


def test_queries_generate_unique_ids() -> None:
    first = ListGeographicRegionsQuery()
    second = ListGeographicRegionsQuery()

    assert first.query_id != second.query_id
