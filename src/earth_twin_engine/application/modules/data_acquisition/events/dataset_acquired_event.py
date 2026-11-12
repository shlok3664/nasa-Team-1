"""Event published after successful dataset acquisition."""

from dataclasses import dataclass
from uuid import UUID

from earth_twin_engine.application.events.application_event import (
    ApplicationEvent,
)
from earth_twin_engine.domain.datasets.dataset import Dataset


@dataclass(frozen=True, slots=True, kw_only=True)
class DatasetAcquiredEvent(ApplicationEvent):
    """Indicates that a dataset was successfully acquired."""

    command_id: UUID
    dataset: Dataset

    def __post_init__(self) -> None:
        super(DatasetAcquiredEvent, self).__post_init__()

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID")

        if not isinstance(self.dataset, Dataset):
            raise TypeError("dataset must be a Dataset")
