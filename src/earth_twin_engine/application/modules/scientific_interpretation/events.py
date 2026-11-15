"""Events emitted by the scientific interpretation module."""

from dataclasses import dataclass
from uuid import UUID

from earth_twin_engine.application.events.application_event import ApplicationEvent

from .scientific_interpretation_models import ScientificInterpretation


@dataclass(frozen=True, slots=True, kw_only=True)
class ScientificInterpretationCompletedEvent(ApplicationEvent):
    """Published when a scientific explanation is generated."""

    source_event_id: UUID
    source_event_type: str
    correlation_id: UUID | None = None
    result: ScientificInterpretation | None = None

    def __post_init__(self) -> None:
        ApplicationEvent.__post_init__(self)

        if not isinstance(self.source_event_id, UUID):
            raise TypeError("source_event_id must be a UUID")

        if not isinstance(self.source_event_type, str) or not self.source_event_type.strip():
            raise ValueError("source_event_type must be a non-empty string")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None")

        if self.result is not None and not isinstance(self.result, ScientificInterpretation):
            raise TypeError("result must be a ScientificInterpretation or None")


@dataclass(frozen=True, slots=True, kw_only=True)
class ScientificInterpretationFailedEvent(ApplicationEvent):
    """Published when a scientific interpretation cannot be generated."""

    source_event_id: UUID | None = None
    source_event_type: str | None = None
    correlation_id: UUID | None = None
    error_type: str = ""
    error_message: str = ""

    def __post_init__(self) -> None:
        ApplicationEvent.__post_init__(self)

        if self.source_event_id is not None and not isinstance(self.source_event_id, UUID):
            raise TypeError("source_event_id must be a UUID or None")

        if self.source_event_type is not None and (
            not isinstance(self.source_event_type, str) or not self.source_event_type.strip()
        ):
            raise ValueError("source_event_type must be a non-empty string or None")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None")

        if not isinstance(self.error_type, str) or not self.error_type.strip():
            raise ValueError("error_type must be a non-empty string")

        if not isinstance(self.error_message, str):
            raise TypeError("error_message must be a string")
