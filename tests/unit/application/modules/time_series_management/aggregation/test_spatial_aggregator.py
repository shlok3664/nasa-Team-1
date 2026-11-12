"""Tests for spatial aggregation."""

from datetime import UTC, datetime, timedelta

import pytest

from earth_twin_engine.application.modules.time_series_management.aggregation import (
    AggregationMethod,
    SpatialAggregator,
)
from earth_twin_engine.domain.geography import SpatialCoordinate
from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import TimeSeries, TimeSeriesPoint


def make_series(series_id, variable, latitude, longitude, values):
    start = datetime(2026, 1, 1, tzinfo=UTC)

    return TimeSeries(
        series_id=series_id,
        variable=variable,
        location=SpatialCoordinate(latitude=latitude, longitude=longitude),
        temporal_resolution=TemporalResolution.DAILY,
        points=tuple(
            TimeSeriesPoint(
                timestamp=start + timedelta(days=index),
                value=value,
            )
            for index, value in enumerate(values)
        ),
    )


def test_aggregate_multiple_locations(variable) -> None:
    first = make_series("north_station", variable, 21.0, 79.0, (10.0, 20.0))
    second = make_series("south_station", variable, 19.0, 77.0, (30.0, 40.0))

    result = SpatialAggregator().aggregate(
        (first, second),
        series_id="regional_temperature",
    )

    assert result.series_id == "regional_temperature"
    assert result.temporal_resolution is TemporalResolution.DAILY
    assert [point.value for point in result.points] == [20.0, 30.0]
    assert result.location.latitude == 20.0
    assert result.location.longitude == 78.0
    assert result.aggregation_metadata is not None
    assert result.aggregation_metadata.input_observation_count == 4
    assert result.aggregation_metadata.output_observation_count == 2


def test_spatial_sum(variable) -> None:
    first = make_series("station_one", variable, 20.0, 78.0, (10.0,))
    second = make_series("station_two", variable, 21.0, 79.0, (15.0,))

    result = SpatialAggregator().aggregate(
        (first, second),
        series_id="regional_sum",
        method=AggregationMethod.SUM,
    )

    assert result.points[0].value == 25.0
    assert result.aggregation_metadata is not None
    assert result.aggregation_metadata.method == "spatial_sum"


def test_reject_single_series(variable) -> None:
    series = make_series("only_station", variable, 20.0, 78.0, (10.0,))

    with pytest.raises(ValueError, match="at least two"):
        SpatialAggregator().aggregate((series,), "invalid_result")


def test_reject_different_variables(variable) -> None:
    from earth_twin_engine.domain.variables import EarthVariable

    other_variable = EarthVariable(
        variable_id="rainfall",
        name="Rainfall",
        description="Precipitation.",
        category=variable.category,
        metadata=variable.metadata,
    )
    first = make_series("station_one", variable, 20.0, 78.0, (10.0,))
    second = make_series("station_two", other_variable, 21.0, 79.0, (15.0,))

    with pytest.raises(ValueError, match="same variable"):
        SpatialAggregator().aggregate((first, second), "invalid_result")


def test_reject_different_resolutions(variable, location) -> None:
    from earth_twin_engine.domain.time_series import TimeSeries

    hourly = TimeSeries(
        series_id="hourly_station",
        variable=variable,
        location=location,
        temporal_resolution=TemporalResolution.HOURLY,
        points=(
            TimeSeriesPoint(
                timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                value=10.0,
            ),
        ),
    )
    daily = make_series("daily_station", variable, 21.0, 79.0, (15.0,))

    with pytest.raises(ValueError, match="same temporal resolution"):
        SpatialAggregator().aggregate((hourly, daily), "invalid_result")
