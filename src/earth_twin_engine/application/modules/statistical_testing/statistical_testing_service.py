"""Application service for executing registered statistical tests."""

from math import isfinite

from earth_twin_engine.domain.time_series import TimeSeries

from .statistical_test_method import StatisticalTestMethod
from .statistical_test_registry import StatisticalTestRegistry
from .statistical_test_result import StatisticalTestResult


class StatisticalTestingService:
    """Executes statistical tests through the registered test strategies."""

    def __init__(self, registry: StatisticalTestRegistry) -> None:
        if not isinstance(registry, StatisticalTestRegistry):
            raise TypeError("registry must be a StatisticalTestRegistry.")

        self._registry = registry

    @property
    def registry(self) -> StatisticalTestRegistry:
        return self._registry

    def run(
        self,
        method: StatisticalTestMethod,
        series: tuple[TimeSeries, ...],
        significance_level: float = 0.05,
        reference_value: float | None = None,
    ) -> StatisticalTestResult:
        if not isinstance(method, StatisticalTestMethod):
            raise TypeError("method must be a StatisticalTestMethod.")

        if not isinstance(series, tuple) or not series:
            raise ValueError("series must be a non-empty tuple of TimeSeries objects.")

        if any(not isinstance(item, TimeSeries) for item in series):
            raise TypeError("Every item in series must be a TimeSeries.")

        if (
            not isinstance(significance_level, (int, float))
            or isinstance(significance_level, bool)
            or not isfinite(significance_level)
            or not 0.0 < significance_level < 1.0
        ):
            raise ValueError("significance_level must be finite and between 0 and 1.")

        statistical_test = self._registry.get(method)

        return statistical_test.run(
            series=series,
            significance_level=float(significance_level),
            reference_value=reference_value,
        )
