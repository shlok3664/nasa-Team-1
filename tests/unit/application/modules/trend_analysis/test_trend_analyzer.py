"""Tests for statistical trend analysis."""

from datetime import UTC, datetime, timedelta

import pytest

from earth_twin_engine.application.modules.trend_analysis import (
    TrendAnalyzer,
    TrendDirection,
    TrendStrength,
)
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
        description="Daily surface temperature.",
        category=next(iter(VariableCategory)),
        metadata=VariableMetadata(
            unit="degC",
            temporal_resolutions=(TemporalResolution.DAILY,),
        ),
    )


def create_series(
    variable: EarthVariable,
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
        series_id="temperature_series",
        variable=variable,
        location=SpatialCoordinate(latitude=20.0, longitude=78.0),
        temporal_resolution=TemporalResolution.DAILY,
        points=points,
    )


def test_analyzer_detects_significant_increasing_trend(
    variable: EarthVariable,
) -> None:
    series = create_series(variable, [10.0, 12.0, 14.0, 16.0, 18.0, 20.0])

    result = TrendAnalyzer().analyze(series)

    assert result.direction == TrendDirection.INCREASING
    assert result.strength == TrendStrength.VERY_STRONG
    assert result.linear_slope_per_day == pytest.approx(2.0)
    assert result.sen_slope_per_day == pytest.approx(2.0)
    assert result.coefficient_of_determination == pytest.approx(1.0)
    assert result.kendall_tau == pytest.approx(1.0)
    assert result.p_value < 0.05


def test_analyzer_detects_significant_decreasing_trend(
    variable: EarthVariable,
) -> None:
    series = create_series(variable, [20.0, 18.0, 16.0, 14.0, 12.0, 10.0])

    result = TrendAnalyzer().analyze(series)

    assert result.direction == TrendDirection.DECREASING
    assert result.linear_slope_per_day == pytest.approx(-2.0)
    assert result.sen_slope_per_day == pytest.approx(-2.0)
    assert result.kendall_tau == pytest.approx(-1.0)


def test_analyzer_classifies_constant_series_as_stable(
    variable: EarthVariable,
) -> None:
    series = create_series(variable, [15.0, 15.0, 15.0, 15.0, 15.0])

    result = TrendAnalyzer().analyze(series)

    assert result.direction == TrendDirection.STABLE
    assert result.linear_slope_per_day == pytest.approx(0.0)
    assert result.sen_slope_per_day == pytest.approx(0.0)
    assert result.p_value == pytest.approx(1.0)


def test_analyzer_ignores_missing_observations(
    variable: EarthVariable,
) -> None:
    series = create_series(
        variable,
        [10.0, None, 14.0, 16.0, None, 20.0],
    )

    result = TrendAnalyzer().analyze(series)

    assert result.direction == TrendDirection.STABLE
    assert result.linear_slope_per_day == pytest.approx(2.0)
    assert result.sen_slope_per_day == pytest.approx(2.0)
    assert result.kendall_tau == pytest.approx(1.0)
    assert result.p_value > result.significance_level


def test_analyzer_reports_insufficient_data(
    variable: EarthVariable,
) -> None:
    series = create_series(variable, [10.0, None, 12.0])

    result = TrendAnalyzer().analyze(series)

    assert result.direction == TrendDirection.INSUFFICIENT_DATA
    assert result.strength == TrendStrength.UNDETERMINED
    assert result.valid_observation_count == 2
    assert result.linear_slope_per_day is None
    assert result.p_value is None


def test_analyzer_rejects_invalid_series() -> None:
    with pytest.raises(TypeError, match="TimeSeries"):
        TrendAnalyzer().analyze("not-a-series")  # type: ignore[arg-type]


@pytest.mark.parametrize("significance_level", [0.0, 1.0, -0.1, 1.1, float("nan")])
def test_analyzer_rejects_invalid_significance_level(
    significance_level: float,
) -> None:
    from earth_twin_engine.application.modules.trend_analysis import (
        InvalidTrendConfigurationError,
    )

    with pytest.raises(InvalidTrendConfigurationError):
        TrendAnalyzer(significance_level=significance_level)
