"""Event subscription identity."""

from dataclasses import dataclass
from uuid import UUID

from earth_twin_engine.application.events.application_event import (
    ApplicationEvent,
)


@dataclass(frozen=True, slots=True)
class EventSubscription:
    """Identifies a handler subscription to an event type."""

    subscription_id: UUID
    event_type: type[ApplicationEvent]

    def __post_init__(self) -> None:
        if not isinstance(self.subscription_id, UUID):
            raise TypeError("subscription_id must be a UUID")

        if not isinstance(self.event_type, type) or not issubclass(
            self.event_type, ApplicationEvent
        ):
            raise TypeError("event_type must inherit from ApplicationEvent")
