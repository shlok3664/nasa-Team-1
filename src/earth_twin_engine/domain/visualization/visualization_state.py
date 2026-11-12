"""Scientific visualization state value object."""

from dataclasses import dataclass

from earth_twin_engine.domain.geography import GeographicRegion
from earth_twin_engine.domain.temporal import TemporalRange
from earth_twin_engine.domain.variables import EarthVariable
from earth_twin_engine.domain.visualization.visualization_type import (
    VisualizationType,
)


@dataclass(frozen=True, slots=True)
class VisualizationState:
    """Describes the data and options represented by a scientific view.

    This contract is independent of any charting, mapping, or UI framework.
    """

    variable: EarthVariable
    temporal_range: TemporalRange
    visualization_type: VisualizationType
    regions: tuple[GeographicRegion, ...]
    show_trend_line: bool = False
    show_confidence_interval: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.variable, EarthVariable):
            raise TypeError("variable must be an EarthVariable")

        if not isinstance(self.temporal_range, TemporalRange):
            raise TypeError("temporal_range must be a TemporalRange")

        if not isinstance(self.visualization_type, VisualizationType):
            raise TypeError("visualization_type must be a VisualizationType")

        if not isinstance(self.regions, tuple):
            raise TypeError("regions must be a tuple")

        if not self.regions:
            raise ValueError("at least one geographic region is required")

        region_ids: set[str] = set()

        for region in self.regions:
            if not isinstance(region, GeographicRegion):
                raise TypeError("regions must contain GeographicRegion values")

            if region.region_id in region_ids:
                raise ValueError("regions cannot contain duplicates")

            region_ids.add(region.region_id)

        if (
            self.visualization_type is VisualizationType.REGIONAL_COMPARISON
            and len(self.regions) < 2
        ):
            raise ValueError("regional comparison requires at least two regions")

        if not isinstance(self.show_trend_line, bool):
            raise TypeError("show_trend_line must be a boolean")

        if not isinstance(self.show_confidence_interval, bool):
            raise TypeError("show_confidence_interval must be a boolean")
