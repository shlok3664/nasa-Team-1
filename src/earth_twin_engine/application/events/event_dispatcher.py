"""Thread-safe event subscription and dispatch."""

from collections.abc import Callable
from threading import RLock
from uuid import uuid4

from earth_twin_engine.application.events.application_event import (
    ApplicationEvent,
)
from earth_twin_engine.application.events.event_dispatch_failure import (
    EventDispatchFailure,
)
from earth_twin_engine.application.events.event_dispatch_result import (
    EventDispatchResult,
)
from earth_twin_engine.application.events.event_subscription import (
    EventSubscription,
)


class EventDispatcher:
    """Publishes events to subscribed handlers."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._handlers: dict[
            type[ApplicationEvent],
            dict[EventSubscription, Callable[[ApplicationEvent], None]],
        ] = {}

    def subscribe(
        self,
        event_type: type[ApplicationEvent],
        handler: Callable[[ApplicationEvent], None],
    ) -> EventSubscription:
        """Subscribe a handler to an event type."""

        if not isinstance(event_type, type) or not issubclass(event_type, ApplicationEvent):
            raise TypeError("event_type must inherit from ApplicationEvent")

        if not callable(handler):
            raise TypeError("handler must be callable")

        subscription = EventSubscription(
            subscription_id=uuid4(),
            event_type=event_type,
        )

        with self._lock:
            self._handlers.setdefault(event_type, {})[subscription] = handler

        return subscription

    def unsubscribe(self, subscription: EventSubscription) -> bool:
        """Remove a subscription. Returns whether it existed."""

        if not isinstance(subscription, EventSubscription):
            raise TypeError("subscription must be an EventSubscription")

        with self._lock:
            handlers = self._handlers.get(subscription.event_type)

            if handlers is None or subscription not in handlers:
                return False

            del handlers[subscription]

            if not handlers:
                del self._handlers[subscription.event_type]

            return True

    def publish(self, event: ApplicationEvent) -> EventDispatchResult:
        """Dispatch an event to matching handlers.

        Handler failures are collected rather than interrupting dispatch.
        Handlers are invoked outside the lock to avoid blocking subscriptions
        and other dispatcher operations.
        """

        if not isinstance(event, ApplicationEvent):
            raise TypeError("event must be an ApplicationEvent")

        with self._lock:
            handlers = [
                (subscription, handler)
                for event_type, subscriptions in self._handlers.items()
                if isinstance(event, event_type)
                for subscription, handler in subscriptions.items()
            ]

        failures: list[EventDispatchFailure] = []

        for subscription, handler in handlers:
            try:
                handler(event)
            except Exception as error:
                failures.append(
                    EventDispatchFailure(
                        subscription_id=subscription.subscription_id,
                        event_type=subscription.event_type,
                        exception=error,
                    )
                )

        return EventDispatchResult(
            event=event,
            dispatched_count=len(handlers),
            failures=tuple(failures),
        )

    @property
    def subscription_count(self) -> int:
        with self._lock:
            return sum(len(handlers) for handlers in self._handlers.values())
