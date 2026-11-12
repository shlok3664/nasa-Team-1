"""Immutable regional comparison results."""

from dataclasses import dataclass
from math import isfinite

from earth_twin_engine.application.modules.trend_analysis.trend_analysis_result import (
    TrendAnalysisResult,
    TrendDirection,
)
from earth_twin_engine.domain.geography import GeographicRegion
from earth_twin_engine.domain.temporal import TemporalResolution


@dataclass(frozen=True, slots=True)
class RegionalTrendResult:
    """Aggregated trend information for one geographic region."""

    region: GeographicRegion
    variable_id: str
    temporal_resolution: TemporalResolution
    series_results: tuple[TrendAnalysisResult, ...]
    mean_linear_slope_per_day: float | None
    mean_sen_slope_per_day: float | None
    mean_kendall_tau: float | None
    direction: TrendDirection
    increasing_series_count: int
    decreasing_series_count: int
    stable_series_count: int
    insufficient_series_count: int
    significant_series_count: int
    total_observation_count: int
    valid_observation_count: int
    missing_observation_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.region, GeographicRegion):
            raise TypeError("region must be a GeographicRegion")

        if not isinstance(self.variable_id, str) or not self.variable_id.strip():
            raise ValueError("variable_id must be a non-empty string")

        if not isinstance(self.temporal_resolution, TemporalResolution):
            raise TypeError("temporal_resolution must be a TemporalResolution")

        if not isinstance(self.series_results, tuple) or not self.series_results:
            raise ValueError("series_results must be a non-empty tuple")

        if not all(isinstance(item, TrendAnalysisResult) for item in self.series_results):
            raise TypeError("series_results must contain TrendAnalysisResult values")

        if not isinstance(self.direction, TrendDirection):
            raise TypeError("direction must be a TrendDirection")

        metrics = (
            self.mean_linear_slope_per_day,
            self.mean_sen_slope_per_day,
            self.mean_kendall_tau,
        )

        for value in metrics:
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
            ):
                raise ValueError("Regional trend metrics must be finite or None")

        if self.mean_kendall_tau is not None and not -1 <= self.mean_kendall_tau <= 1:
            raise ValueError("mean_kendall_tau must be between -1 and 1")

        counts = (
            self.increasing_series_count,
            self.decreasing_series_count,
            self.stable_series_count,
            self.insufficient_series_count,
            self.significant_series_count,
            self.total_observation_count,
            self.valid_observation_count,
            self.missing_observation_count,
        )

        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in counts
        ):
            raise ValueError("Regional counts must be non-negative integers")

        if sum(
            (
                self.increasing_series_count,
                self.decreasing_series_count,
                self.stable_series_count,
                self.insufficient_series_count,
            )
        ) != len(self.series_results):
            raise ValueError("Trend direction counts must match the number of series")

        if self.significant_series_count > len(self.series_results):
            raise ValueError("significant_series_count cannot exceed the series count")

        if self.valid_observation_count + self.missing_observation_count != (
            self.total_observation_count
        ):
            raise ValueError("Valid and missing counts must equal total observations")


@dataclass(frozen=True, slots=True)
class RegionalComparisonResult:
    """Comparison of multiple geographic regions for one Earth variable."""

    variable_id: str
    temporal_resolution: TemporalResolution
    regions: tuple[RegionalTrendResult, ...]
    ranking: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.variable_id, str) or not self.variable_id.strip():
            raise ValueError("variable_id must be a non-empty string")

        if not isinstance(self.temporal_resolution, TemporalResolution):
            raise TypeError("temporal_resolution must be a TemporalResolution")

        if not isinstance(self.regions, tuple) or len(self.regions) < 2:
            raise ValueError("A regional comparison requires at least two regions")

        if not all(isinstance(item, RegionalTrendResult) for item in self.regions):
            raise TypeError("regions must contain RegionalTrendResult values")

        region_ids = tuple(item.region.region_id for item in self.regions)

        if len(set(region_ids)) != len(region_ids):
            raise ValueError("A region may appear only once in a comparison")

        if not isinstance(self.ranking, tuple) or set(self.ranking) != set(region_ids):
            raise ValueError("ranking must contain every compared region exactly once")
