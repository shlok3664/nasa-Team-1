"""Immutable statistical test result."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

from .statistical_test_method import StatisticalTestMethod


@dataclass(frozen=True, slots=True)
class StatisticalTestResult:
    """Stores a statistical test outcome and its supporting information."""

    method: StatisticalTestMethod
    series_ids: tuple[str, ...]
    statistic: float
    p_value: float
    significance_level: float
    significant: bool
    estimate: float
    degrees_of_freedom: float | None
    sample_sizes: tuple[int, ...]
    valid_observation_counts: tuple[int, ...]
    missing_observation_counts: tuple[int, ...]
    confidence_interval: tuple[float, float] | None
    assumptions: tuple[str, ...]
    warnings: tuple[str, ...]
    analyzed_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.method, StatisticalTestMethod):
            raise TypeError("method must be a StatisticalTestMethod.")

        if not isinstance(self.series_ids, tuple) or not self.series_ids:
            raise ValueError("series_ids must be a non-empty tuple.")

        if any(not isinstance(value, str) or not value.strip() for value in self.series_ids):
            raise ValueError("Every series ID must be a non-empty string.")

        if len(set(self.series_ids)) != len(self.series_ids):
            raise ValueError("series_ids must be unique.")

        numeric_values = {
            "statistic": self.statistic,
            "p_value": self.p_value,
            "significance_level": self.significance_level,
            "estimate": self.estimate,
        }

        for name, value in numeric_values.items():
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not isfinite(value)
            ):
                raise ValueError(f"{name} must be finite.")

        if not 0.0 <= self.p_value <= 1.0:
            raise ValueError("p_value must be between 0 and 1.")

        if not 0.0 < self.significance_level < 1.0:
            raise ValueError("significance_level must be between 0 and 1.")

        if not isinstance(self.significant, bool):
            raise TypeError("significant must be a boolean.")

        if self.significant != (self.p_value < self.significance_level):
            raise ValueError("significant must agree with the p-value and threshold.")

        if self.degrees_of_freedom is not None and (
            not isfinite(self.degrees_of_freedom) or self.degrees_of_freedom <= 0.0
        ):
            raise ValueError("degrees_of_freedom must be positive and finite or None.")

        count_groups = (
            self.sample_sizes,
            self.valid_observation_counts,
            self.missing_observation_counts,
        )

        for counts in count_groups:
            if not isinstance(counts, tuple) or len(counts) != len(self.series_ids):
                raise ValueError("Observation count tuples must match series_ids.")

            if any(
                not isinstance(count, int) or isinstance(count, bool) or count < 0
                for count in counts
            ):
                raise ValueError("Observation counts must be non-negative integers.")

        for sample, valid, missing in zip(
            self.sample_sizes,
            self.valid_observation_counts,
            self.missing_observation_counts,
            strict=True,
        ):
            if valid + missing != sample:
                raise ValueError("Valid and missing counts must equal sample size.")

        if self.confidence_interval is not None:
            if (
                not isinstance(self.confidence_interval, tuple)
                or len(self.confidence_interval) != 2
            ):
                raise ValueError("confidence_interval must contain two values.")

            lower, upper = self.confidence_interval
            if not isfinite(lower) or not isfinite(upper) or lower > upper:
                raise ValueError("Confidence interval bounds must be finite and ordered.")

        if not isinstance(self.assumptions, tuple) or not all(
            isinstance(item, str) and item.strip() for item in self.assumptions
        ):
            raise TypeError("assumptions must be a tuple of non-empty strings.")

        if not isinstance(self.warnings, tuple) or not all(
            isinstance(item, str) and item.strip() for item in self.warnings
        ):
            raise TypeError("warnings must be a tuple of non-empty strings.")

        if not isinstance(self.analyzed_at, datetime):
            raise TypeError("analyzed_at must be a datetime.")

        if self.analyzed_at.tzinfo is None or self.analyzed_at.utcoffset() is None:
            raise ValueError("analyzed_at must be timezone-aware.")
