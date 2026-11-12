"""Comparison of scientific trends across geographic regions."""

from dataclasses import dataclass

from earth_twin_engine.domain.temporal import TemporalRange
from earth_twin_engine.domain.trends.regional_trend import RegionalTrend
from earth_twin_engine.domain.variables import EarthVariable


@dataclass(frozen=True, slots=True)
class RegionalComparison:
    """Compares a variable's trend across multiple geographic regions."""

    variable: EarthVariable
    temporal_range: TemporalRange
    regional_trends: tuple[RegionalTrend, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.variable, EarthVariable):
            raise TypeError("variable must be an EarthVariable")

        if not isinstance(self.temporal_range, TemporalRange):
            raise TypeError("temporal_range must be a TemporalRange")

        if not isinstance(self.regional_trends, tuple):
            raise TypeError("regional_trends must be a tuple")

        if len(self.regional_trends) < 2:
            raise ValueError("regional comparison requires at least two regions")

        region_ids: set[str] = set()

        for regional_trend in self.regional_trends:
            if not isinstance(regional_trend, RegionalTrend):
                raise TypeError("regional_trends must contain RegionalTrend values")

            if regional_trend.region.region_id in region_ids:
                raise ValueError("regional comparison cannot contain duplicate regions")

            region_ids.add(regional_trend.region.region_id)

            if regional_trend.result.variable != self.variable:
                raise ValueError("all regional trends must use the same variable")

            if regional_trend.result.temporal_range != self.temporal_range:
                raise ValueError("all regional trends must use the same temporal range")
