"""Scientific time-series domain entity."""

import re
from dataclasses import dataclass

from earth_twin_engine.domain.geography import SpatialCoordinate
from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series.aggregation_metadata import (
    AggregationMetadata,
)
from earth_twin_engine.domain.time_series.time_series_point import TimeSeriesPoint
from earth_twin_engine.domain.variables import EarthVariable

_SERIES_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class TimeSeries:
    """Represents observations of an Earth variable at a location."""

    series_id: str
    variable: EarthVariable
    location: SpatialCoordinate
    temporal_resolution: TemporalResolution
    points: tuple[TimeSeriesPoint, ...]
    aggregation_metadata: AggregationMetadata | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.series_id, str):
            raise TypeError("series_id must be a string")

        if not _SERIES_ID_PATTERN.fullmatch(self.series_id):
            raise ValueError(
                "series_id must use lowercase letters, numbers, "
                "and underscores, starting with a letter"
            )

        if not isinstance(self.variable, EarthVariable):
            raise TypeError("variable must be an EarthVariable")

        if not isinstance(self.location, SpatialCoordinate):
            raise TypeError("location must be a SpatialCoordinate")

        if not isinstance(self.temporal_resolution, TemporalResolution):
            raise TypeError("temporal_resolution must be a TemporalResolution")

        if self.temporal_resolution not in self.variable.metadata.temporal_resolutions:
            raise ValueError("temporal resolution is not supported by the variable metadata")

        if not isinstance(self.points, tuple):
            raise TypeError("points must be a tuple")

        if not self.points:
            raise ValueError("a time series must contain at least one point")

        if self.aggregation_metadata is not None and not isinstance(
            self.aggregation_metadata, AggregationMetadata
        ):
            raise TypeError("aggregation_metadata must be an AggregationMetadata or None")

        previous_timestamp = None

        for point in self.points:
            if not isinstance(point, TimeSeriesPoint):
                raise TypeError("points must contain TimeSeriesPoint values")

            if previous_timestamp is not None and point.timestamp <= previous_timestamp:
                raise ValueError("points must have strictly increasing timestamps")

            previous_timestamp = point.timestamp

    @property
    def observation_count(self) -> int:
        """Return the total number of observations."""

        return len(self.points)

    @property
    def valid_observation_count(self) -> int:
        """Return the number of observations with actual values."""

        return sum(point.value is not None for point in self.points)

    @property
    def missing_observation_count(self) -> int:
        """Return the number of observations with missing values."""

        return sum(point.value is None for point in self.points)

    @property
    def start_timestamp(self):
        """Return the first observation timestamp."""

        return self.points[0].timestamp

    @property
    def end_timestamp(self):
        """Return the last observation timestamp."""

        return self.points[-1].timestamp
