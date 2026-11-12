"""Scientific metadata associated with Earth variables."""

from dataclasses import dataclass
from math import isfinite

from earth_twin_engine.domain.temporal import (
    TemporalRange,
    TemporalResolution,
)


@dataclass(frozen=True, slots=True)
class VariableMetadata:
    """Describes the scientific and observational properties of a variable."""

    unit: str
    temporal_resolutions: tuple[TemporalResolution, ...]
    spatial_resolution_meters: float | None = None
    temporal_coverage: TemporalRange | None = None
    keywords: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.unit, str) or not self.unit.strip():
            raise ValueError("unit must be a non-empty string")

        if not isinstance(self.temporal_resolutions, tuple):
            raise TypeError("temporal_resolutions must be a tuple")

        if not self.temporal_resolutions:
            raise ValueError("at least one temporal resolution is required")

        if not all(
            isinstance(resolution, TemporalResolution) for resolution in self.temporal_resolutions
        ):
            raise TypeError("temporal_resolutions must contain TemporalResolution values")

        if len(set(self.temporal_resolutions)) != len(self.temporal_resolutions):
            raise ValueError("temporal_resolutions must not contain duplicates")

        if self.spatial_resolution_meters is not None:
            resolution = self.spatial_resolution_meters

            if isinstance(resolution, bool) or not isinstance(resolution, (int, float)):
                raise TypeError("spatial resolution must be a numeric value")

            if not isfinite(resolution) or resolution <= 0:
                raise ValueError("spatial resolution must be finite and positive")

        if self.temporal_coverage is not None and not isinstance(
            self.temporal_coverage, TemporalRange
        ):
            raise TypeError("temporal_coverage must be a TemporalRange")

        self._validate_string_collection(self.keywords, "keywords")
        self._validate_string_collection(self.source_ids, "source_ids")

    @staticmethod
    def _validate_string_collection(
        values: tuple[str, ...],
        field_name: str,
    ) -> None:
        if not isinstance(values, tuple):
            raise TypeError(f"{field_name} must be a tuple")

        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError(f"{field_name} must contain non-empty strings")

        if len(set(values)) != len(values):
            raise ValueError(f"{field_name} must not contain duplicates")
