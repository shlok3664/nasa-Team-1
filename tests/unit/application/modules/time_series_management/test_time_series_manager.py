"""Tests for the time-series manager."""

import pytest

from earth_twin_engine.application.modules.time_series_management import (
    DuplicateTimeSeriesError,
    TimeSeriesManager,
    TimeSeriesNotFoundError,
)


def test_register_and_get_series(hourly_series) -> None:
    manager = TimeSeriesManager()

    manager.register(hourly_series)

    assert manager.get(hourly_series.series_id) is hourly_series
    assert manager.count == 1


def test_reject_duplicate_series(hourly_series) -> None:
    manager = TimeSeriesManager()
    manager.register(hourly_series)

    with pytest.raises(DuplicateTimeSeriesError):
        manager.register(hourly_series)


def test_unregister_series(hourly_series) -> None:
    manager = TimeSeriesManager()
    manager.register(hourly_series)

    assert manager.unregister(hourly_series.series_id) is True
    assert manager.unregister(hourly_series.series_id) is False
    assert manager.count == 0


def test_get_unknown_series() -> None:
    manager = TimeSeriesManager()

    with pytest.raises(TimeSeriesNotFoundError):
        manager.get("unknown_series")


def test_get_all_series(hourly_series) -> None:
    manager = TimeSeriesManager()
    manager.register(hourly_series)

    assert manager.get_all() == (hourly_series,)


def test_find_by_variable(hourly_series) -> None:
    manager = TimeSeriesManager()
    manager.register(hourly_series)

    result = manager.find_by_variable("air_temperature")

    assert result == (hourly_series,)


def test_contains_series(hourly_series) -> None:
    manager = TimeSeriesManager()

    assert manager.contains(hourly_series.series_id) is False

    manager.register(hourly_series)

    assert manager.contains(hourly_series.series_id) is True
