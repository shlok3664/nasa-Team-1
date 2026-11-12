"""Result of publishing an application event."""

from dataclasses import dataclass

from earth_twin_engine.application.events.application_event import (
    ApplicationEvent,
)
from earth_twin_engine.application.events.event_dispatch_failure import (
    EventDispatchFailure,
)


@dataclass(frozen=True, slots=True)
class EventDispatchResult:
    """Summarizes successful and failed event handler executions."""

    event: ApplicationEvent
    dispatched_count: int
    failures: tuple[EventDispatchFailure, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.event, ApplicationEvent):
            raise TypeError("event must be an ApplicationEvent")

        if (
            isinstance(self.dispatched_count, bool)
            or not isinstance(self.dispatched_count, int)
            or self.dispatched_count < 0
        ):
            raise ValueError("dispatched_count must be a non-negative integer")

        if not isinstance(self.failures, tuple):
            raise TypeError("failures must be a tuple")

        if any(not isinstance(failure, EventDispatchFailure) for failure in self.failures):
            raise TypeError("failures must contain EventDispatchFailure instances")

    @property
    def succeeded_count(self) -> int:
        return self.dispatched_count - len(self.failures)

    @property
    def failed_count(self) -> int:
        return len(self.failures)

    @property
    def successful(self) -> bool:
        return not self.failures
