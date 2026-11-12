"""Scientific trend analysis result."""

from dataclasses import dataclass

from earth_twin_engine.domain.geography import GeographicRegion
from earth_twin_engine.domain.temporal import TemporalRange
from earth_twin_engine.domain.trends.confidence_interval import (
    ConfidenceInterval,
)
from earth_twin_engine.domain.trends.significance_result import (
    SignificanceResult,
)
from earth_twin_engine.domain.trends.statistical_test_result import (
    StatisticalTestResult,
)
from earth_twin_engine.domain.trends.trend_direction import TrendDirection
from earth_twin_engine.domain.trends.trend_slope import TrendSlope
from earth_twin_engine.domain.variables import EarthVariable


@dataclass(frozen=True, slots=True)
class TrendResult:
    """Represents an estimated trend for an Earth science variable."""

    variable: EarthVariable
    region: GeographicRegion
    temporal_range: TemporalRange
    slope: TrendSlope
    direction: TrendDirection
    sample_count: int
    confidence_interval: ConfidenceInterval | None = None
    statistical_test: StatisticalTestResult | None = None
    significance: SignificanceResult | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.variable, EarthVariable):
            raise TypeError("variable must be an EarthVariable")

        if not isinstance(self.region, GeographicRegion):
            raise TypeError("region must be a GeographicRegion")

        if not isinstance(self.temporal_range, TemporalRange):
            raise TypeError("temporal_range must be a TemporalRange")

        if not isinstance(self.slope, TrendSlope):
            raise TypeError("slope must be a TrendSlope")

        if not isinstance(self.direction, TrendDirection):
            raise TypeError("direction must be a TrendDirection")

        if isinstance(self.sample_count, bool) or not isinstance(self.sample_count, int):
            raise TypeError("sample_count must be an integer")

        if self.sample_count < 2:
            raise ValueError("sample_count must be at least 2")

        if self.direction is TrendDirection.INCREASING and self.slope.value <= 0:
            raise ValueError("increasing trend requires a positive slope")

        if self.direction is TrendDirection.DECREASING and self.slope.value >= 0:
            raise ValueError("decreasing trend requires a negative slope")

        if self.direction is TrendDirection.STABLE and self.slope.value != 0:
            raise ValueError("stable trend requires a zero slope")

        if self.confidence_interval is not None and not isinstance(
            self.confidence_interval, ConfidenceInterval
        ):
            raise TypeError("confidence_interval must be a ConfidenceInterval or None")

        if self.statistical_test is not None and not isinstance(
            self.statistical_test, StatisticalTestResult
        ):
            raise TypeError("statistical_test must be a StatisticalTestResult or None")

        if self.significance is not None and not isinstance(self.significance, SignificanceResult):
            raise TypeError("significance must be a SignificanceResult or None")

        if (
            self.statistical_test is not None
            and self.significance is not None
            and self.statistical_test.significance != self.significance
        ):
            raise ValueError("significance must match the statistical test result")
