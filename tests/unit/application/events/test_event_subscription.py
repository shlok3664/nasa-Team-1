from uuid import uuid4

import pytest

from earth_twin_engine.application.events import (
    ApplicationEvent,
    EventSubscription,
)


class ExampleEvent(ApplicationEvent):
    pass


class InvalidEvent:
    pass


def test_create_valid_subscription() -> None:
    subscription_id = uuid4()

    subscription = EventSubscription(
        subscription_id=subscription_id,
        event_type=ExampleEvent,
    )

    assert subscription.subscription_id == subscription_id
    assert subscription.event_type is ExampleEvent


def test_reject_invalid_subscription_id() -> None:
    with pytest.raises(TypeError):
        EventSubscription(
            subscription_id="invalid",
            event_type=ExampleEvent,
        )


def test_reject_invalid_event_type() -> None:
    with pytest.raises(TypeError):
        EventSubscription(
            subscription_id=uuid4(),
            event_type=InvalidEvent,
        )


def test_subscription_is_immutable() -> None:
    subscription = EventSubscription(
        subscription_id=uuid4(),
        event_type=ExampleEvent,
    )

    with pytest.raises(AttributeError):
        subscription.event_type = InvalidEvent
