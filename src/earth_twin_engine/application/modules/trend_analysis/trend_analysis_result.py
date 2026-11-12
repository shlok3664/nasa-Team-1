"""Immutable result of a time-series trend analysis."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from math import isfinite

from earth_twin_engine.domain.temporal import TemporalResolution


class TrendDirection(StrEnum):
    """Direction of an observed time-series trend."""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    INSUFFICIENT_DATA = "insufficient_data"


class TrendStrength(StrEnum):
    """Strength of a monotonic trend based on Kendall's tau."""

    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"
    UNDETERMINED = "undetermined"


@dataclass(frozen=True, slots=True)
class TrendAnalysisResult:
    """Statistical trend metrics for one time series."""

    series_id: str
    variable_id: str
    temporal_resolution: TemporalResolution
    direction: TrendDirection
    strength: TrendStrength
    input_observation_count: int
    valid_observation_count: int
    missing_observation_count: int
    linear_slope_per_day: float | None
    sen_slope_per_day: float | None
    linear_intercept_at_start: float | None
    coefficient_of_determination: float | None
    kendall_tau: float | None
    p_value: float | None
    significance_level: float
    analyzed_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.series_id, str) or not self.series_id.strip():
            raise ValueError("series_id must be a non-empty string.")

        if not isinstance(self.variable_id, str) or not self.variable_id.strip():
            raise ValueError("variable_id must be a non-empty string.")

        if not isinstance(self.temporal_resolution, TemporalResolution):
            raise TypeError("temporal_resolution must be a TemporalResolution.")

        if not isinstance(self.direction, TrendDirection):
            raise TypeError("direction must be a TrendDirection.")

        if not isinstance(self.strength, TrendStrength):
            raise TypeError("strength must be a TrendStrength.")

        counts = (
            self.input_observation_count,
            self.valid_observation_count,
            self.missing_observation_count,
        )

        if any(
            not isinstance(count, int) or isinstance(count, bool) or count < 0 for count in counts
        ):
            raise ValueError("Observation counts must be non-negative integers.")

        if (
            self.valid_observation_count + self.missing_observation_count
            != self.input_observation_count
        ):
            raise ValueError("Valid and missing counts must equal the input count.")

        if not isinstance(self.significance_level, (int, float)):
            raise TypeError("significance_level must be numeric.")

        if not 0.0 < self.significance_level < 1.0:
            raise ValueError("significance_level must be between 0 and 1.")

        metric_names = (
            "linear_slope_per_day",
            "sen_slope_per_day",
            "linear_intercept_at_start",
            "coefficient_of_determination",
            "kendall_tau",
            "p_value",
        )

        for name in metric_names:
            value = getattr(self, name)
            if value is not None and (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not isfinite(value)
            ):
                raise ValueError(f"{name} must be finite or None.")

        if self.coefficient_of_determination is not None and not (
            0.0 <= self.coefficient_of_determination <= 1.0
        ):
            raise ValueError("coefficient_of_determination must be between 0 and 1.")

        if self.kendall_tau is not None and not -1.0 <= self.kendall_tau <= 1.0:
            raise ValueError("kendall_tau must be between -1 and 1.")

        if self.p_value is not None and not 0.0 <= self.p_value <= 1.0:
            raise ValueError("p_value must be between 0 and 1.")

        if not isinstance(self.analyzed_at, datetime):
            raise TypeError("analyzed_at must be a datetime.")

        if self.analyzed_at.tzinfo is None or self.analyzed_at.utcoffset() is None:
            raise ValueError("analyzed_at must be timezone-aware.")
