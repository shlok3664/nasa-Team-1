"""Scientific data request value object."""

from dataclasses import dataclass

from earth_twin_engine.domain.geography import GeographicRegion
from earth_twin_engine.domain.temporal import (
    TemporalRange,
    TemporalResolution,
)
from earth_twin_engine.domain.variables import EarthVariable


@dataclass(frozen=True, slots=True)
class DataRequest:
    """Describes a request for Earth science observations."""

    variable: EarthVariable
    region: GeographicRegion
    temporal_range: TemporalRange
    temporal_resolution: TemporalResolution
    source_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.variable, EarthVariable):
            raise TypeError("variable must be an EarthVariable")

        if not isinstance(self.region, GeographicRegion):
            raise TypeError("region must be a GeographicRegion")

        if not isinstance(self.temporal_range, TemporalRange):
            raise TypeError("temporal_range must be a TemporalRange")

        if not isinstance(self.temporal_resolution, TemporalResolution):
            raise TypeError("temporal_resolution must be a TemporalResolution")

        if self.temporal_resolution not in self.variable.metadata.temporal_resolutions:
            raise ValueError(
                "requested temporal resolution is not supported by the variable metadata"
            )

        if self.source_id is not None:
            if not isinstance(self.source_id, str) or not self.source_id.strip():
                raise ValueError("source_id must be a non-empty string")
