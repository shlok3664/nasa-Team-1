"""Metadata describing scientific time-series aggregation."""

from dataclasses import dataclass
from datetime import datetime

from earth_twin_engine.domain.temporal import TemporalResolution


@dataclass(frozen=True, slots=True)
class AggregationMetadata:
    """Records the method and scope of an aggregation operation."""

    method: str
    source_resolution: TemporalResolution
    target_resolution: TemporalResolution
    input_observation_count: int
    output_observation_count: int
    missing_observation_count: int
    applied_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.method, str) or not self.method.strip():
            raise ValueError("method must be a non-empty string")

        if not isinstance(self.source_resolution, TemporalResolution):
            raise TypeError("source_resolution must be a TemporalResolution")

        if not isinstance(self.target_resolution, TemporalResolution):
            raise TypeError("target_resolution must be a TemporalResolution")

        for name, value in (
            ("input_observation_count", self.input_observation_count),
            ("output_observation_count", self.output_observation_count),
            ("missing_observation_count", self.missing_observation_count),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")

            if value < 0:
                raise ValueError(f"{name} cannot be negative")

        if self.missing_observation_count > self.input_observation_count:
            raise ValueError("missing_observation_count cannot exceed input_observation_count")

        if self.output_observation_count > self.input_observation_count:
            raise ValueError("output_observation_count cannot exceed input_observation_count")

        if not isinstance(self.applied_at, datetime):
            raise TypeError("applied_at must be a datetime")

        if self.applied_at.tzinfo is None or self.applied_at.utcoffset() is None:
            raise ValueError("applied_at must be timezone-aware")

    @property
    def valid_input_observation_count(self) -> int:
        """Return the number of input observations with actual values."""

        return self.input_observation_count - self.missing_observation_count
