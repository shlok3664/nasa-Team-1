"""Shared fixtures for trend domain tests."""

from datetime import UTC, datetime

import pytest

from earth_twin_engine.domain.geography import (
    GeographicRegion,
    SpatialBoundary,
)
from earth_twin_engine.domain.temporal import (
    TemporalRange,
    TemporalResolution,
)
from earth_twin_engine.domain.variables import (
    EarthVariable,
    VariableCategory,
    VariableMetadata,
)


@pytest.fixture
def trend_variable() -> EarthVariable:
    return EarthVariable(
        variable_id="air_temperature",
        name="Air Temperature",
        description="Near-surface atmospheric air temperature.",
        category=VariableCategory.ATMOSPHERE,
        metadata=VariableMetadata(
            unit="K",
            temporal_resolutions=(TemporalResolution.ANNUAL,),
        ),
    )


@pytest.fixture
def trend_region() -> GeographicRegion:
    return GeographicRegion(
        region_id="maharashtra",
        name="Maharashtra",
        boundary=SpatialBoundary(
            south_latitude=15.6,
            north_latitude=22.0,
            west_longitude=72.6,
            east_longitude=80.9,
        ),
    )


@pytest.fixture
def trend_range() -> TemporalRange:
    return TemporalRange(
        start=datetime(2010, 1, 1, tzinfo=UTC),
        end=datetime(2020, 1, 1, tzinfo=UTC),
    )
