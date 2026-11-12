"""Shared fixtures for visualization domain tests."""

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
from earth_twin_engine.domain.visualization import VisualizationType


@pytest.fixture
def visualization_variable() -> EarthVariable:
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
def visualization_region() -> GeographicRegion:
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
def second_visualization_region() -> GeographicRegion:
    return GeographicRegion(
        region_id="gujarat",
        name="Gujarat",
        boundary=SpatialBoundary(
            south_latitude=20.1,
            north_latitude=24.7,
            west_longitude=68.1,
            east_longitude=74.5,
        ),
    )


@pytest.fixture
def visualization_range() -> TemporalRange:
    return TemporalRange(
        start=datetime(2010, 1, 1, tzinfo=UTC),
        end=datetime(2020, 1, 1, tzinfo=UTC),
    )


@pytest.fixture
def visualization_type() -> VisualizationType:
    return VisualizationType.TIME_SERIES
