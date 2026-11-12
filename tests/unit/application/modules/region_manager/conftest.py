import pytest

from earth_twin_engine.domain.geography import (
    GeographicRegion,
    SpatialBoundary,
    SpatialCoordinate,
)


@pytest.fixture
def india_region() -> GeographicRegion:
    return GeographicRegion(
        region_id="india",
        name="India",
        description="Geographic boundary covering India.",
        boundary=SpatialBoundary(
            south_latitude=6.0,
            north_latitude=37.0,
            west_longitude=68.0,
            east_longitude=98.0,
        ),
    )


@pytest.fixture
def maharashtra_region() -> GeographicRegion:
    return GeographicRegion(
        region_id="maharashtra",
        name="Maharashtra",
        description="Geographic boundary covering Maharashtra.",
        boundary=SpatialBoundary(
            south_latitude=15.5,
            north_latitude=22.5,
            west_longitude=72.5,
            east_longitude=80.9,
        ),
    )


@pytest.fixture
def japan_region() -> GeographicRegion:
    return GeographicRegion(
        region_id="japan",
        name="Japan",
        description="Geographic boundary covering Japan.",
        boundary=SpatialBoundary(
            south_latitude=24.0,
            north_latitude=46.0,
            west_longitude=122.0,
            east_longitude=146.0,
        ),
    )


@pytest.fixture
def nagpur_coordinate() -> SpatialCoordinate:
    return SpatialCoordinate(
        latitude=21.1458,
        longitude=79.0882,
    )
