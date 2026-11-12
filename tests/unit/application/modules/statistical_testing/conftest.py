"""Shared fixtures for statistical testing."""

from collections.abc import Callable
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
        variable_id="surface_temperature",
        name="Surface Temperature",
        description="Environmental surface temperature.",
        category=next(iter(VariableCategory)),
        metadata=VariableMetadata(
            unit="degC",
            temporal_resolutions=(TemporalResolution.DAILY,),
        ),
    )


@pytest.fixture
def make_series(
    variable: EarthVariable,
) -> Callable[[str, list[float | None]], TimeSeries]:
    def create(
        series_id: str,
        values: list[float | None],
    ) -> TimeSeries:
        start = datetime(2025, 1, 1, tzinfo=UTC)

        points = tuple(
            TimeSeriesPoint(
                timestamp=start + timedelta(days=index),
                value=value,
            )
            for index, value in enumerate(values)
        )

        return TimeSeries(
            series_id=series_id,
            variable=variable,
            location=SpatialCoordinate(
                latitude=20.0,
                longitude=78.0,
            ),
            temporal_resolution=TemporalResolution.DAILY,
            points=points,
        )

    return create
