"""Event published after scientific dataset validation."""

from dataclasses import dataclass
from uuid import UUID

from earth_twin_engine.application.events.application_event import (
    ApplicationEvent,
)
from earth_twin_engine.application.modules.data_validation.validation_result import (
    ValidationResult,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class DatasetValidatedEvent(ApplicationEvent):
    """Reports the result of a dataset validation operation."""

    command_id: UUID
    correlation_id: UUID | None = None
    dataset_id: str
    validation_result: ValidationResult

    def __post_init__(self) -> None:
        super(DatasetValidatedEvent, self).__post_init__()

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID.")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None.")

        if not isinstance(self.dataset_id, str) or not self.dataset_id.strip():
            raise ValueError("dataset_id must be a non-empty string.")

        if not isinstance(self.validation_result, ValidationResult):
            raise TypeError("validation_result must be a ValidationResult instance.")
