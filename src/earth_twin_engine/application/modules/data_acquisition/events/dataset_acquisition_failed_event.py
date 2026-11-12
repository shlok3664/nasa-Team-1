"""Event published when dataset acquisition fails."""

from dataclasses import dataclass
from uuid import UUID

from earth_twin_engine.application.events.application_event import (
    ApplicationEvent,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class DatasetAcquisitionFailedEvent(ApplicationEvent):
    """Describes a failed dataset acquisition attempt."""

    command_id: UUID
    variable_id: str
    region_id: str
    exception: Exception

    def __post_init__(self) -> None:
        super(DatasetAcquisitionFailedEvent, self).__post_init__()

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID")

        for field_name, value in (
            ("variable_id", self.variable_id),
            ("region_id", self.region_id),
        ):
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string")

            if not value.strip():
                raise ValueError(f"{field_name} cannot be empty or whitespace")

        if not isinstance(self.exception, Exception):
            raise TypeError("exception must be an Exception")
