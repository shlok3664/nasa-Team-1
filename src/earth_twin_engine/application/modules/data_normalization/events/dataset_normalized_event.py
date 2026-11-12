"""Event published after scientific dataset normalization."""

from dataclasses import dataclass
from uuid import UUID

from earth_twin_engine.application.events.application_event import ApplicationEvent
from earth_twin_engine.application.modules.data_normalization.normalization_result import (
    NormalizationResult,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class DatasetNormalizedEvent(ApplicationEvent):
    """Reports the result of a dataset normalization operation."""

    command_id: UUID
    correlation_id: UUID | None = None
    dataset_id: str
    normalization_result: NormalizationResult

    def __post_init__(self) -> None:
        super(DatasetNormalizedEvent, self).__post_init__()

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID.")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None.")

        if not isinstance(self.dataset_id, str) or not self.dataset_id.strip():
            raise ValueError("dataset_id must be a non-empty string.")

        if not isinstance(self.normalization_result, NormalizationResult):
            raise TypeError("normalization_result must be a NormalizationResult instance.")
