from dataclasses import dataclass

import pytest

from earth_twin_engine.application.events import (
    ApplicationEvent,
    EventDispatcher,
)


@dataclass(frozen=True, slots=True)
class ExampleEvent(ApplicationEvent):
    value: int = 10


@dataclass(frozen=True, slots=True)
class SpecializedEvent(ExampleEvent):
    label: str = "specialized"


@dataclass(frozen=True, slots=True)
class OtherEvent(ApplicationEvent):
    pass


class InvalidEvent:
    pass


def test_subscribe_handler(dispatcher: EventDispatcher) -> None:
    subscription = dispatcher.subscribe(ExampleEvent, lambda event: None)

    assert subscription.event_type is ExampleEvent
    assert dispatcher.subscription_count == 1


def test_reject_invalid_event_type(dispatcher: EventDispatcher) -> None:
    with pytest.raises(TypeError):
        dispatcher.subscribe(InvalidEvent, lambda event: None)


def test_reject_non_callable_handler(dispatcher: EventDispatcher) -> None:
    with pytest.raises(TypeError):
        dispatcher.subscribe(ExampleEvent, "not callable")


def test_multiple_subscribers_receive_event(
    dispatcher: EventDispatcher,
) -> None:
    received: list[ExampleEvent] = []

    event = ExampleEvent()

    dispatcher.subscribe(ExampleEvent, received.append)
    dispatcher.subscribe(ExampleEvent, received.append)

    result = dispatcher.publish(event)

    assert received == [event, event]
    assert result.dispatched_count == 2
    assert result.succeeded_count == 2
    assert result.failed_count == 0
    assert result.successful


def test_unrelated_event_is_not_dispatched(
    dispatcher: EventDispatcher,
) -> None:
    received: list[ExampleEvent] = []

    dispatcher.subscribe(ExampleEvent, received.append)

    result = dispatcher.publish(OtherEvent())

    assert received == []
    assert result.dispatched_count == 0
    assert result.successful


def test_subclass_event_reaches_base_subscription(
    dispatcher: EventDispatcher,
) -> None:
    received: list[ExampleEvent] = []

    dispatcher.subscribe(ExampleEvent, received.append)

    event = SpecializedEvent()
    result = dispatcher.publish(event)

    assert received == [event]
    assert result.dispatched_count == 1


def test_unsubscribe_handler(
    dispatcher: EventDispatcher,
) -> None:
    received: list[ExampleEvent] = []

    subscription = dispatcher.subscribe(ExampleEvent, received.append)

    assert dispatcher.unsubscribe(subscription)
    assert not dispatcher.unsubscribe(subscription)

    event = ExampleEvent()
    dispatcher.publish(event)

    assert received == []
    assert dispatcher.subscription_count == 0


def test_reject_invalid_subscription_on_unsubscribe(
    dispatcher: EventDispatcher,
) -> None:
    with pytest.raises(TypeError):
        dispatcher.unsubscribe("invalid")


def test_handler_failure_does_not_interrupt_dispatch(
    dispatcher: EventDispatcher,
) -> None:
    received: list[ExampleEvent] = []

    def failing_handler(event: ExampleEvent) -> None:
        raise RuntimeError("handler failed")

    dispatcher.subscribe(ExampleEvent, failing_handler)
    dispatcher.subscribe(ExampleEvent, received.append)

    event = ExampleEvent()
    result = dispatcher.publish(event)

    assert received == [event]
    assert result.dispatched_count == 2
    assert result.succeeded_count == 1
    assert result.failed_count == 1
    assert not result.successful
    assert isinstance(result.failures[0].exception, RuntimeError)


def test_dispatch_failure_identifies_subscription(
    dispatcher: EventDispatcher,
) -> None:
    subscription = dispatcher.subscribe(
        ExampleEvent,
        lambda event: (_ for _ in ()).throw(ValueError("failure")),
    )

    result = dispatcher.publish(ExampleEvent())

    assert result.failures[0].subscription_id == subscription.subscription_id
    assert result.failures[0].event_type is ExampleEvent


def test_reject_non_event_on_publish(
    dispatcher: EventDispatcher,
) -> None:
    with pytest.raises(TypeError):
        dispatcher.publish(InvalidEvent())


def test_dispatcher_handles_no_subscribers(
    dispatcher: EventDispatcher,
) -> None:
    result = dispatcher.publish(ExampleEvent())

    assert result.dispatched_count == 0
    assert result.failed_count == 0
    assert result.successful


def test_subscription_changes_apply_to_next_dispatch(
    dispatcher: EventDispatcher,
) -> None:
    received: list[str] = []

    second_subscription = None

    def first_handler(event: ExampleEvent) -> None:
        received.append("first")

        if second_subscription is not None:
            dispatcher.unsubscribe(second_subscription)

    dispatcher.subscribe(ExampleEvent, first_handler)
    second_subscription = dispatcher.subscribe(
        ExampleEvent,
        lambda event: received.append("second"),
    )

    dispatcher.publish(ExampleEvent())

    assert received == ["first", "second"]

    received.clear()
    dispatcher.publish(ExampleEvent())

    assert received == ["first"]


def test_subscription_count_tracks_all_handlers(
    dispatcher: EventDispatcher,
) -> None:
    first = dispatcher.subscribe(ExampleEvent, lambda event: None)
    second = dispatcher.subscribe(OtherEvent, lambda event: None)

    assert dispatcher.subscription_count == 2

    dispatcher.unsubscribe(first)

    assert dispatcher.subscription_count == 1

    dispatcher.unsubscribe(second)

    assert dispatcher.subscription_count == 0
