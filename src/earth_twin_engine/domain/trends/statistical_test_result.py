"""Scientific statistical test result."""

from dataclasses import dataclass
from math import isfinite

from earth_twin_engine.domain.trends.significance_result import (
    SignificanceResult,
)


@dataclass(frozen=True, slots=True)
class StatisticalTestResult:
    """Stores the result of a statistical test."""

    test_name: str
    statistic_name: str
    statistic_value: float
    sample_count: int
    significance: SignificanceResult

    def __post_init__(self) -> None:
        for name, value in (
            ("test_name", self.test_name),
            ("statistic_name", self.statistic_name),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        if isinstance(self.statistic_value, bool) or not isinstance(
            self.statistic_value, (int, float)
        ):
            raise TypeError("statistic_value must be numeric")

        if not isfinite(self.statistic_value):
            raise ValueError("statistic_value must be finite")

        if isinstance(self.sample_count, bool) or not isinstance(self.sample_count, int):
            raise TypeError("sample_count must be an integer")

        if self.sample_count < 1:
            raise ValueError("sample_count must be positive")

        if not isinstance(self.significance, SignificanceResult):
            raise TypeError("significance must be a SignificanceResult")
