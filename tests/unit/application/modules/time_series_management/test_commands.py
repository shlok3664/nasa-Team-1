"""Tests for time-series management commands."""

import pytest

from earth_twin_engine.application.modules.time_series_management import (
    AggregateSpatialTimeSeriesCommand,
    AggregateTimeSeriesCommand,
    AggregationMethod,
    RegisterTimeSeriesCommand,
    RemoveTimeSeriesCommand,
)
from earth_twin_engine.domain.temporal import TemporalResolution


def test_create_register_command(hourly_series) -> None:
    command = RegisterTimeSeriesCommand(series=hourly_series)

    assert command.series is hourly_series
    assert command.command_id is not None


def test_reject_invalid_register_command() -> None:
    with pytest.raises(TypeError, match="TimeSeries"):
        RegisterTimeSeriesCommand(series="invalid")  # type: ignore[arg-type]


def test_create_remove_command() -> None:
    command = RemoveTimeSeriesCommand(series_id="temperature_hourly")

    assert command.series_id == "temperature_hourly"


def test_reject_empty_remove_identifier() -> None:
    with pytest.raises(ValueError, match="series_id"):
        RemoveTimeSeriesCommand(series_id=" ")


def test_create_temporal_aggregation_command() -> None:
    command = AggregateTimeSeriesCommand(
        series_id="temperature_hourly",
        target_resolution=TemporalResolution.DAILY,
        method=AggregationMethod.MEAN,
    )

    assert command.target_resolution is TemporalResolution.DAILY
    assert command.method is AggregationMethod.MEAN


def test_reject_invalid_temporal_resolution() -> None:
    with pytest.raises(TypeError, match="TemporalResolution"):
        AggregateTimeSeriesCommand(
            series_id="temperature_hourly",
            target_resolution="daily",  # type: ignore[arg-type]
        )


def test_create_spatial_aggregation_command() -> None:
    command = AggregateSpatialTimeSeriesCommand(
        series_ids=("station_one", "station_two"),
        result_series_id="regional_temperature",
    )

    assert len(command.series_ids) == 2
    assert command.result_series_id == "regional_temperature"


def test_reject_duplicate_spatial_source_ids() -> None:
    with pytest.raises(ValueError, match="duplicates"):
        AggregateSpatialTimeSeriesCommand(
            series_ids=("station_one", "station_one"),
            result_series_id="regional_temperature",
        )
