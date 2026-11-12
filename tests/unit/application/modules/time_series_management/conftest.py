"""Shared fixtures for time-series management tests."""

from datetime import UTC, datetime, timedelta

import pytest

from earth_twin_engine.domain.geography import SpatialCoordinate
from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import TimeSeries, TimeSeriesPoint
from earth_twin_engine.domain.variables import (
    EarthVariable,
    VariableCategory,
    VariableMetadata,
)


@pytest.fixture
def variable() -> EarthVariable:
    return EarthVariable(
        variable_id="air_temperature",
        name="Air Temperature",
        description="Near-surface air temperature.",
        category=next(iter(VariableCategory)),
        metadata=VariableMetadata(
            unit="K",
            temporal_resolutions=tuple(TemporalResolution),
        ),
    )


@pytest.fixture
def location() -> SpatialCoordinate:
    return SpatialCoordinate(latitude=20.5937, longitude=78.9629)


@pytest.fixture
def hourly_series(variable, location) -> TimeSeries:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    return TimeSeries(
        series_id="temperature_hourly",
        variable=variable,
        location=location,
        temporal_resolution=TemporalResolution.HOURLY,
        points=tuple(
            TimeSeriesPoint(
                timestamp=start + timedelta(hours=index),
                value=None if index == 2 else float(index + 270),
            )
            for index in range(48)
        ),
    )
