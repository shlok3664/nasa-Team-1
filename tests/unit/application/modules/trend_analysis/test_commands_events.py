"""Tests for trend analysis commands and events."""

from uuid import uuid4

import pytest

from earth_twin_engine.application.modules.trend_analysis import (
    AnalyzeTimeSeriesTrendCommand,
    TrendAnalysisCompletedEvent,
    TrendAnalysisFailedEvent,
    TrendDirection,
    TrendStrength,
)
from earth_twin_engine.domain.temporal import TemporalResolution


def test_analyze_command_accepts_valid_series_id() -> None:
    command = AnalyzeTimeSeriesTrendCommand(series_id="temperature_series")

    assert command.series_id == "temperature_series"
    assert isinstance(command.command_id, type(uuid4()))


@pytest.mark.parametrize("series_id", ["", " ", None])
def test_analyze_command_rejects_invalid_series_id(
    series_id: str | None,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        AnalyzeTimeSeriesTrendCommand(series_id=series_id)  # type: ignore[arg-type]


def test_completed_event_rejects_invalid_result() -> None:
    with pytest.raises(TypeError, match="TrendAnalysisResult"):
        TrendAnalysisCompletedEvent(
            command_id=uuid4(),
            correlation_id=None,
            result=None,  # type: ignore[arg-type]
        )


def test_failed_event_rejects_empty_series_id() -> None:
    with pytest.raises(ValueError, match="series_id"):
        TrendAnalysisFailedEvent(
            command_id=uuid4(),
            correlation_id=None,
            series_id=" ",
            error_type="ValueError",
            error_message="Invalid input.",
        )


def test_result_contains_analysis_metadata() -> None:
    from datetime import UTC, datetime

    from earth_twin_engine.application.modules.trend_analysis import (
        TrendAnalysisResult,
    )

    result = TrendAnalysisResult(
        series_id="temperature_series",
        variable_id="surface_temperature",
        temporal_resolution=TemporalResolution.DAILY,
        direction=TrendDirection.STABLE,
        strength=TrendStrength.VERY_WEAK,
        input_observation_count=3,
        valid_observation_count=3,
        missing_observation_count=0,
        linear_slope_per_day=0.0,
        sen_slope_per_day=0.0,
        linear_intercept_at_start=15.0,
        coefficient_of_determination=1.0,
        kendall_tau=0.0,
        p_value=1.0,
        significance_level=0.05,
        analyzed_at=datetime.now(UTC),
    )

    assert result.series_id == "temperature_series"
    assert result.input_observation_count == 3
    assert result.missing_observation_count == 0
