from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from earth_twin_engine.application.events import ApplicationEvent


class ExampleEvent(ApplicationEvent):
    pass


def test_event_generates_identity_and_timestamp() -> None:
    event = ExampleEvent()

    assert event.event_id is not None
    assert event.occurred_at.tzinfo is not None
    assert event.correlation_id is None


def test_event_generates_unique_ids() -> None:
    first = ExampleEvent()
    second = ExampleEvent()

    assert first.event_id != second.event_id


def test_event_accepts_correlation_id() -> None:
    correlation_id = uuid4()

    event = ExampleEvent(correlation_id=correlation_id)

    assert event.correlation_id == correlation_id


def test_reject_invalid_event_id() -> None:
    with pytest.raises(TypeError):
        ExampleEvent(event_id="invalid")


def test_reject_naive_timestamp() -> None:
    with pytest.raises(ValueError):
        ExampleEvent(occurred_at=datetime(2026, 1, 1))


def test_reject_invalid_timestamp_type() -> None:
    with pytest.raises(TypeError):
        ExampleEvent(occurred_at="2026-01-01")


def test_reject_invalid_correlation_id() -> None:
    with pytest.raises(TypeError):
        ExampleEvent(correlation_id="invalid")


def test_event_is_immutable() -> None:
    event = ExampleEvent()

    with pytest.raises(FrozenInstanceError):
        event.event_id = uuid4()


def test_event_accepts_timezone_aware_timestamp() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    event = ExampleEvent(occurred_at=timestamp)

    assert event.occurred_at == timestamp
