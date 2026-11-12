"""Tests for temporal aggregation."""

from datetime import UTC, datetime

import pytest

from earth_twin_engine.application.modules.time_series_management.aggregation import (
    AggregationMethod,
    TemporalAggregator,
)
from earth_twin_engine.domain.temporal import TemporalResolution


def test_aggregate_hourly_series_to_daily(hourly_series) -> None:
    result = TemporalAggregator().aggregate(
        hourly_series,
        TemporalResolution.DAILY,
    )

    assert result.temporal_resolution is TemporalResolution.DAILY
    assert result.observation_count == 2
    assert result.points[0].timestamp == datetime(2026, 1, 1, tzinfo=UTC)
    assert result.points[1].timestamp == datetime(2026, 1, 2, tzinfo=UTC)
    assert result.aggregation_metadata is not None
    assert result.aggregation_metadata.method == "mean"
    assert result.aggregation_metadata.input_observation_count == 48
    assert result.aggregation_metadata.output_observation_count == 2
    assert result.aggregation_metadata.missing_observation_count == 1


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        (AggregationMethod.SUM, 6.0),
        (AggregationMethod.MINIMUM, 1.0),
        (AggregationMethod.MAXIMUM, 3.0),
        (AggregationMethod.MEDIAN, 2.0),
        (AggregationMethod.MEAN, 2.0),
    ],
)
def test_aggregation_methods(method, expected, variable, location) -> None:
    from earth_twin_engine.domain.time_series import TimeSeries, TimeSeriesPoint

    series = TimeSeries(
        series_id="method_test",
        variable=variable,
        location=location,
        temporal_resolution=TemporalResolution.HOURLY,
        points=tuple(
            TimeSeriesPoint(
                timestamp=datetime(2026, 1, 1, hour, tzinfo=UTC),
                value=value,
            )
            for hour, value in enumerate((1.0, 2.0, 3.0))
        ),
    )

    result = TemporalAggregator().aggregate(
        series,
        TemporalResolution.DAILY,
        method,
    )

    assert result.points[0].value == expected


def test_preserve_all_missing_bucket(variable, location) -> None:
    from earth_twin_engine.domain.time_series import TimeSeries, TimeSeriesPoint

    series = TimeSeries(
        series_id="missing_test",
        variable=variable,
        location=location,
        temporal_resolution=TemporalResolution.HOURLY,
        points=(
            TimeSeriesPoint(
                timestamp=datetime(2026, 1, 1, 1, tzinfo=UTC),
                value=None,
            ),
            TimeSeriesPoint(
                timestamp=datetime(2026, 1, 1, 2, tzinfo=UTC),
                value=None,
            ),
        ),
    )

    result = TemporalAggregator().aggregate(
        series,
        TemporalResolution.DAILY,
    )

    assert result.observation_count == 1
    assert result.points[0].value is None


def test_reject_same_resolution(hourly_series) -> None:
    with pytest.raises(ValueError, match="coarser"):
        TemporalAggregator().aggregate(
            hourly_series,
            TemporalResolution.HOURLY,
        )


def test_reject_irregular_target(hourly_series) -> None:
    with pytest.raises(ValueError, match="irregular"):
        TemporalAggregator().aggregate(
            hourly_series,
            TemporalResolution.IRREGULAR,
        )


def test_reject_unsupported_target(variable, location) -> None:
    from dataclasses import replace

    from earth_twin_engine.domain.time_series import TimeSeries, TimeSeriesPoint

    restricted_variable = replace(
        variable,
        metadata=replace(
            variable.metadata,
            temporal_resolutions=(TemporalResolution.HOURLY,),
        ),
    )
    series = TimeSeries(
        series_id="restricted_series",
        variable=restricted_variable,
        location=location,
        temporal_resolution=TemporalResolution.HOURLY,
        points=(
            TimeSeriesPoint(
                timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                value=280.0,
            ),
        ),
    )

    with pytest.raises(ValueError, match="not supported"):
        TemporalAggregator().aggregate(series, TemporalResolution.DAILY)
