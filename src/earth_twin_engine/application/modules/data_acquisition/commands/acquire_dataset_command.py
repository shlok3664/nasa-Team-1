"""Command requesting acquisition of an Earth science dataset."""

from dataclasses import dataclass

from earth_twin_engine.application.commands.application_command import (
    ApplicationCommand,
)
from earth_twin_engine.domain.temporal.temporal_range import TemporalRange
from earth_twin_engine.domain.temporal.temporal_resolution import (
    TemporalResolution,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class AcquireDatasetCommand(ApplicationCommand):
    """Request a dataset for a variable, region, and temporal interval."""

    variable_id: str
    region_id: str
    temporal_range: TemporalRange
    temporal_resolution: TemporalResolution
    source_id: str | None = None

    def __post_init__(self) -> None:
        super(AcquireDatasetCommand, self).__post_init__()

        for field_name, value in (
            ("variable_id", self.variable_id),
            ("region_id", self.region_id),
        ):
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string")

            if not value.strip():
                raise ValueError(f"{field_name} cannot be empty or whitespace")

        if not isinstance(self.temporal_range, TemporalRange):
            raise TypeError("temporal_range must be a TemporalRange")

        if not isinstance(self.temporal_resolution, TemporalResolution):
            raise TypeError("temporal_resolution must be a TemporalResolution")

        if self.source_id is not None:
            if not isinstance(self.source_id, str):
                raise TypeError("source_id must be a string or None")

            if not self.source_id.strip():
                raise ValueError("source_id cannot be empty or whitespace")
