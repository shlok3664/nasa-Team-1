"""Tests for individual time-series observations."""

from datetime import UTC, datetime

import pytest

from earth_twin_engine.domain.time_series import TimeSeriesPoint


def test_create_valid_observation() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    point = TimeSeriesPoint(timestamp=timestamp, value=298.5)

    assert point.timestamp == timestamp
    assert point.value == 298.5


def test_allow_missing_observation() -> None:
    point = TimeSeriesPoint(
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        value=None,
    )

    assert point.value is None


def test_allow_zero_as_a_real_measurement() -> None:
    point = TimeSeriesPoint(
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        value=0.0,
    )

    assert point.value == 0.0


def test_reject_non_datetime_timestamp() -> None:
    with pytest.raises(TypeError, match="datetime"):
        TimeSeriesPoint(timestamp="2026-01-01", value=10)  # type: ignore[arg-type]


def test_reject_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        TimeSeriesPoint(
            timestamp=datetime(2026, 1, 1),
            value=10,
        )


def test_reject_non_numeric_value() -> None:
    with pytest.raises(TypeError, match="numeric"):
        TimeSeriesPoint(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            value="298.5",  # type: ignore[arg-type]
        )


def test_reject_boolean_value() -> None:
    with pytest.raises(TypeError, match="numeric"):
        TimeSeriesPoint(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            value=True,
        )


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_reject_non_finite_value(value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        TimeSeriesPoint(
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            value=value,
        )


def test_observation_is_immutable() -> None:
    point = TimeSeriesPoint(
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        value=10,
    )

    with pytest.raises(AttributeError):
        point.value = 20  # type: ignore[misc]
