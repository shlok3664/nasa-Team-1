"""Tests for temporal range contracts."""

from datetime import UTC, datetime, timedelta

import pytest

from earth_twin_engine.domain.temporal import TemporalRange


def test_create_valid_temporal_range() -> None:
    start = datetime(2020, 1, 1, tzinfo=UTC)
    end = datetime(2021, 1, 1, tzinfo=UTC)

    temporal_range = TemporalRange(start=start, end=end)

    assert temporal_range.start == start
    assert temporal_range.end == end


def test_reject_naive_start_datetime() -> None:
    with pytest.raises(ValueError, match="start must be timezone-aware"):
        TemporalRange(
            start=datetime(2020, 1, 1),
            end=datetime(2021, 1, 1, tzinfo=UTC),
        )


def test_reject_naive_end_datetime() -> None:
    with pytest.raises(ValueError, match="end must be timezone-aware"):
        TemporalRange(
            start=datetime(2020, 1, 1, tzinfo=UTC),
            end=datetime(2021, 1, 1),
        )


def test_reject_invalid_temporal_order() -> None:
    timestamp = datetime(2020, 1, 1, tzinfo=UTC)

    with pytest.raises(ValueError, match="start must be earlier"):
        TemporalRange(start=timestamp, end=timestamp)


def test_calculate_duration() -> None:
    start = datetime(2020, 1, 1, tzinfo=UTC)
    end = start + timedelta(days=10)

    temporal_range = TemporalRange(start=start, end=end)

    assert temporal_range.duration_seconds == 864000


def test_contains_timestamp() -> None:
    start = datetime(2020, 1, 1, tzinfo=UTC)
    end = datetime(2020, 1, 10, tzinfo=UTC)

    temporal_range = TemporalRange(start=start, end=end)

    assert temporal_range.contains(start)
    assert temporal_range.contains(datetime(2020, 1, 5, tzinfo=UTC))
    assert not temporal_range.contains(end)


def test_reject_naive_timestamp_in_contains() -> None:
    temporal_range = TemporalRange(
        start=datetime(2020, 1, 1, tzinfo=UTC),
        end=datetime(2021, 1, 1, tzinfo=UTC),
    )

    with pytest.raises(ValueError, match="timestamp must be timezone-aware"):
        temporal_range.contains(datetime(2020, 6, 1))
