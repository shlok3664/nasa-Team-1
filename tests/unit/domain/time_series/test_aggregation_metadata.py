"""Tests for time-series aggregation metadata."""

from datetime import UTC, datetime

import pytest

from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import AggregationMetadata


def create_metadata(**overrides: object) -> AggregationMetadata:
    values: dict[str, object] = {
        "method": "mean",
        "source_resolution": TemporalResolution.HOURLY,
        "target_resolution": TemporalResolution.DAILY,
        "input_observation_count": 24,
        "output_observation_count": 1,
        "missing_observation_count": 2,
        "applied_at": datetime(2026, 1, 2, tzinfo=UTC),
    }
    values.update(overrides)

    return AggregationMetadata(**values)  # type: ignore[arg-type]


def test_create_valid_aggregation_metadata() -> None:
    metadata = create_metadata()

    assert metadata.method == "mean"
    assert metadata.source_resolution is TemporalResolution.HOURLY
    assert metadata.target_resolution is TemporalResolution.DAILY


def test_calculate_valid_input_count() -> None:
    metadata = create_metadata()

    assert metadata.valid_input_observation_count == 22


def test_allow_zero_observation_counts() -> None:
    metadata = create_metadata(
        input_observation_count=0,
        output_observation_count=0,
        missing_observation_count=0,
    )

    assert metadata.valid_input_observation_count == 0


def test_reject_empty_method() -> None:
    with pytest.raises(ValueError, match="method"):
        create_metadata(method=" ")


@pytest.mark.parametrize(
    ("field", "expected_error"),
    [
        ("source_resolution", "source_resolution"),
        ("target_resolution", "target_resolution"),
    ],
)
def test_reject_invalid_resolution(
    field: str,
    expected_error: str,
) -> None:
    with pytest.raises(TypeError, match=expected_error):
        create_metadata(**{field: "daily"})


@pytest.mark.parametrize(
    "field",
    [
        "input_observation_count",
        "output_observation_count",
        "missing_observation_count",
    ],
)
def test_reject_negative_counts(field: str) -> None:
    with pytest.raises(ValueError, match="negative"):
        create_metadata(**{field: -1})


@pytest.mark.parametrize(
    "field",
    [
        "input_observation_count",
        "output_observation_count",
        "missing_observation_count",
    ],
)
def test_reject_boolean_counts(field: str) -> None:
    with pytest.raises(TypeError, match="integer"):
        create_metadata(**{field: True})


def test_reject_non_integer_counts() -> None:
    with pytest.raises(TypeError, match="integer"):
        create_metadata(input_observation_count=2.5)


def test_reject_missing_count_greater_than_input_count() -> None:
    with pytest.raises(ValueError, match="missing_observation_count"):
        create_metadata(
            input_observation_count=10,
            missing_observation_count=11,
        )


def test_reject_output_count_greater_than_input_count() -> None:
    with pytest.raises(ValueError, match="output_observation_count"):
        create_metadata(
            input_observation_count=10,
            output_observation_count=11,
        )


def test_reject_non_datetime_applied_at() -> None:
    with pytest.raises(TypeError, match="datetime"):
        create_metadata(applied_at="2026-01-02")


def test_reject_naive_applied_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        create_metadata(applied_at=datetime(2026, 1, 2))


def test_aggregation_metadata_is_immutable() -> None:
    metadata = create_metadata()

    with pytest.raises(AttributeError):
        metadata.method = "sum"  # type: ignore[misc]
