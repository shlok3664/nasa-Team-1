"""Trend result associated with a geographic region."""

from dataclasses import dataclass

from earth_twin_engine.domain.geography import GeographicRegion
from earth_twin_engine.domain.trends.trend_result import TrendResult


@dataclass(frozen=True, slots=True)
class RegionalTrend:
    """Associates a trend result with a geographic region."""

    region: GeographicRegion
    result: TrendResult

    def __post_init__(self) -> None:
        if not isinstance(self.region, GeographicRegion):
            raise TypeError("region must be a GeographicRegion")

        if not isinstance(self.result, TrendResult):
            raise TypeError("result must be a TrendResult")

        if self.region != self.result.region:
            raise ValueError("regional trend region must match the trend result region")
