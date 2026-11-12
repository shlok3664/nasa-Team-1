"""Tests for scientific time series."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from earth_twin_engine.domain.geography import SpatialCoordinate
from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import (
    TimeSeries,
    TimeSeriesPoint,
)
from earth_twin_engine.domain.variables import (
    EarthVariable,
    VariableCategory,
    VariableMetadata,
)


def create_variable() -> EarthVariable:
    return EarthVariable(
        variable_id="air_temperature",
        name="Air Temperature",
        description="Near-surface atmospheric air temperature.",
        category=VariableCategory.ATMOSPHERE,
        metadata=VariableMetadata(
            unit="K",
            temporal_resolutions=(
                TemporalResolution.HOURLY,
                TemporalResolution.DAILY,
            ),
        ),
    )


def create_points() -> tuple[TimeSeriesPoint, ...]:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    return (
        TimeSeriesPoint(start, 298.5),
        TimeSeriesPoint(start + timedelta(hours=1), 299.0),
        TimeSeriesPoint(start + timedelta(hours=2), None),
        TimeSeriesPoint(start + timedelta(hours=3), 297.8),
    )


def create_series(**overrides: object) -> TimeSeries:
    values: dict[str, object] = {
        "series_id": "india_air_temperature",
        "variable": create_variable(),
        "location": SpatialCoordinate(20.5937, 78.9629),
        "temporal_resolution": TemporalResolution.HOURLY,
        "points": create_points(),
    }
    values.update(overrides)

    return TimeSeries(**values)  # type: ignore[arg-type]


def test_create_valid_time_series() -> None:
    series = create_series()

    assert series.series_id == "india_air_temperature"
    assert series.variable.variable_id == "air_temperature"
    assert series.location.latitude == 20.5937
    assert series.temporal_resolution is TemporalResolution.HOURLY


def test_count_observations() -> None:
    series = create_series()

    assert series.observation_count == 4
    assert series.valid_observation_count == 3
    assert series.missing_observation_count == 1


def test_preserve_missing_observations() -> None:
    series = create_series()

    assert series.points[2].value is None
    assert series.points[2].timestamp == datetime(2026, 1, 1, 2, tzinfo=UTC)


def test_get_series_timestamp_bounds() -> None:
    series = create_series()

    assert series.start_timestamp == datetime(2026, 1, 1, tzinfo=UTC)
    assert series.end_timestamp == datetime(2026, 1, 1, 3, tzinfo=UTC)


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("variable", None, "EarthVariable"),
        ("location", None, "SpatialCoordinate"),
        ("temporal_resolution", "hourly", "TemporalResolution"),
    ],
)
def test_reject_invalid_contract_types(
    field: str,
    value: object,
    expected_error: str,
) -> None:
    with pytest.raises(TypeError, match=expected_error):
        create_series(**{field: value})


@pytest.mark.parametrize(
    "series_id",
    ["", "India", "india-temperature", "1series", "india series"],
)
def test_reject_invalid_series_id(series_id: str) -> None:
    with pytest.raises(ValueError, match="series_id"):
        create_series(series_id=series_id)


def test_reject_non_string_series_id() -> None:
    with pytest.raises(TypeError, match="series_id"):
        create_series(series_id=123)


def test_reject_unsupported_temporal_resolution() -> None:
    with pytest.raises(ValueError, match="not supported"):
        create_series(temporal_resolution=TemporalResolution.MONTHLY)


def test_reject_mutable_points_collection() -> None:
    with pytest.raises(TypeError, match="tuple"):
        create_series(points=list(create_points()))


def test_reject_empty_points_collection() -> None:
    with pytest.raises(ValueError, match="at least one"):
        create_series(points=())


def test_reject_invalid_point_type() -> None:
    with pytest.raises(TypeError, match="TimeSeriesPoint"):
        create_series(points=("not a point",))


def test_reject_out_of_order_points() -> None:
    points = create_points()

    with pytest.raises(ValueError, match="increasing"):
        create_series(points=(points[1], points[0]))


def test_reject_duplicate_timestamps() -> None:
    points = create_points()

    with pytest.raises(ValueError, match="increasing"):
        create_series(
            points=(
                points[0],
                TimeSeriesPoint(points[0].timestamp, 300),
            )
        )


def test_compare_timestamps_across_timezones() -> None:
    first = datetime(2026, 1, 1, 5, 30, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    second = datetime(2026, 1, 1, tzinfo=UTC)

    with pytest.raises(ValueError, match="increasing"):
        create_series(
            points=(
                TimeSeriesPoint(first, 298),
                TimeSeriesPoint(second, 299),
            )
        )


def test_time_series_is_immutable() -> None:
    series = create_series()

    with pytest.raises(AttributeError):
        series.series_id = "changed"  # type: ignore[misc]
