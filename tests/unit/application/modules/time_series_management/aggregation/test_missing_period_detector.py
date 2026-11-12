"""Tests for missing calendar-period detection."""

from datetime import UTC, datetime

from earth_twin_engine.application.modules.time_series_management.aggregation import (
    MissingPeriodDetector,
)
from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import TimeSeries, TimeSeriesPoint


def test_detect_missing_daily_periods(variable, location) -> None:
    series = TimeSeries(
        series_id="daily_gaps",
        variable=variable,
        location=location,
        temporal_resolution=TemporalResolution.DAILY,
        points=(
            TimeSeriesPoint(datetime(2026, 1, 1, tzinfo=UTC), 10.0),
            TimeSeriesPoint(datetime(2026, 1, 3, tzinfo=UTC), 12.0),
            TimeSeriesPoint(datetime(2026, 1, 5, tzinfo=UTC), 14.0),
        ),
    )

    missing = MissingPeriodDetector().detect(series)

    assert missing == (
        datetime(2026, 1, 2, tzinfo=UTC),
        datetime(2026, 1, 4, tzinfo=UTC),
    )


def test_detect_missing_months(variable, location) -> None:
    series = TimeSeries(
        series_id="monthly_gaps",
        variable=variable,
        location=location,
        temporal_resolution=TemporalResolution.MONTHLY,
        points=(
            TimeSeriesPoint(datetime(2026, 1, 1, tzinfo=UTC), 10.0),
            TimeSeriesPoint(datetime(2026, 4, 1, tzinfo=UTC), 12.0),
        ),
    )

    assert MissingPeriodDetector().detect(series) == (
        datetime(2026, 2, 1, tzinfo=UTC),
        datetime(2026, 3, 1, tzinfo=UTC),
    )


def test_missing_values_are_not_missing_periods(hourly_series) -> None:
    assert MissingPeriodDetector().detect(hourly_series) == ()


def test_return_empty_when_no_period_is_missing(variable, location) -> None:
    series = TimeSeries(
        series_id="continuous_daily",
        variable=variable,
        location=location,
        temporal_resolution=TemporalResolution.DAILY,
        points=(
            TimeSeriesPoint(datetime(2026, 1, 1, tzinfo=UTC), 10.0),
            TimeSeriesPoint(datetime(2026, 1, 2, tzinfo=UTC), 11.0),
            TimeSeriesPoint(datetime(2026, 1, 3, tzinfo=UTC), 12.0),
        ),
    )

    assert MissingPeriodDetector().detect(series) == ()
