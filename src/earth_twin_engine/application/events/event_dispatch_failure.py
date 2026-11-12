"""Details of an event handler failure."""

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from earth_twin_engine.application.events.application_event import (
        ApplicationEvent,
    )


@dataclass(frozen=True, slots=True)
class EventDispatchFailure:
    """Describes a handler that failed while processing an event."""

    subscription_id: UUID
    event_type: type[ApplicationEvent]
    exception: Exception

    def __post_init__(self) -> None:
        if not isinstance(self.subscription_id, UUID):
            raise TypeError("subscription_id must be a UUID")

        if not isinstance(self.event_type, type):
            raise TypeError("event_type must be a type")

        if not isinstance(self.exception, Exception):
            raise TypeError("exception must be an Exception")
