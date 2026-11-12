"""Statistical trend analysis using regression, Mann-Kendall, and Sen's slope."""

from collections import Counter
from datetime import UTC, datetime
from math import erfc, isfinite, sqrt
from statistics import median

from earth_twin_engine.domain.time_series import TimeSeries

from .errors import InvalidTrendConfigurationError
from .trend_analysis_result import (
    TrendAnalysisResult,
    TrendDirection,
    TrendStrength,
)


class TrendAnalyzer:
    """Calculates statistical trends without external scientific dependencies."""

    def __init__(self, significance_level: float = 0.05) -> None:
        if (
            not isinstance(significance_level, (int, float))
            or isinstance(significance_level, bool)
            or not isfinite(significance_level)
            or not 0.0 < significance_level < 1.0
        ):
            raise InvalidTrendConfigurationError(
                "significance_level must be finite and between 0 and 1."
            )

        self._significance_level = float(significance_level)

    @property
    def significance_level(self) -> float:
        return self._significance_level

    def analyze(self, series: TimeSeries) -> TrendAnalysisResult:
        """Analyze one series, ignoring missing observations."""

        if not isinstance(series, TimeSeries):
            raise TypeError("series must be a TimeSeries.")

        valid_points = [point for point in series.points if point.value is not None]
        missing_count = len(series.points) - len(valid_points)

        if len(valid_points) < 3:
            return TrendAnalysisResult(
                series_id=series.series_id,
                variable_id=series.variable.variable_id,
                temporal_resolution=series.temporal_resolution,
                direction=TrendDirection.INSUFFICIENT_DATA,
                strength=TrendStrength.UNDETERMINED,
                input_observation_count=len(series.points),
                valid_observation_count=len(valid_points),
                missing_observation_count=missing_count,
                linear_slope_per_day=None,
                sen_slope_per_day=None,
                linear_intercept_at_start=None,
                coefficient_of_determination=None,
                kendall_tau=None,
                p_value=None,
                significance_level=self._significance_level,
                analyzed_at=datetime.now(UTC),
            )

        first_timestamp = valid_points[0].timestamp
        x_values = [
            (point.timestamp - first_timestamp).total_seconds() / 86400.0 for point in valid_points
        ]
        y_values = [float(point.value) for point in valid_points]

        slope, intercept, r_squared = self._linear_regression(x_values, y_values)
        sen_slope = self._sen_slope(x_values, y_values)
        kendall_tau, p_value = self._mann_kendall(y_values)

        if p_value < self._significance_level:
            if sen_slope > 0.0:
                direction = TrendDirection.INCREASING
            elif sen_slope < 0.0:
                direction = TrendDirection.DECREASING
            else:
                direction = TrendDirection.STABLE
        else:
            direction = TrendDirection.STABLE

        strength = self._classify_strength(abs(kendall_tau))

        return TrendAnalysisResult(
            series_id=series.series_id,
            variable_id=series.variable.variable_id,
            temporal_resolution=series.temporal_resolution,
            direction=direction,
            strength=strength,
            input_observation_count=len(series.points),
            valid_observation_count=len(valid_points),
            missing_observation_count=missing_count,
            linear_slope_per_day=slope,
            sen_slope_per_day=sen_slope,
            linear_intercept_at_start=intercept,
            coefficient_of_determination=r_squared,
            kendall_tau=kendall_tau,
            p_value=p_value,
            significance_level=self._significance_level,
            analyzed_at=datetime.now(UTC),
        )

    @staticmethod
    def _linear_regression(
        x_values: list[float],
        y_values: list[float],
    ) -> tuple[float, float, float]:
        count = len(x_values)
        mean_x = sum(x_values) / count
        mean_y = sum(y_values) / count

        sum_xx = sum((x - mean_x) ** 2 for x in x_values)
        sum_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, y_values, strict=True))

        if sum_xx == 0.0:
            raise ValueError("Trend analysis requires distinct timestamps.")

        slope = sum_xy / sum_xx
        intercept = mean_y - slope * mean_x

        predicted = [intercept + slope * x for x in x_values]
        residual_sum = sum(
            (actual - estimate) ** 2 for actual, estimate in zip(y_values, predicted, strict=True)
        )
        total_sum = sum((value - mean_y) ** 2 for value in y_values)

        if total_sum == 0.0:
            r_squared = 1.0 if residual_sum == 0.0 else 0.0
        else:
            r_squared = max(0.0, min(1.0, 1.0 - residual_sum / total_sum))

        return slope, intercept, r_squared

    @staticmethod
    def _sen_slope(
        x_values: list[float],
        y_values: list[float],
    ) -> float:
        slopes = [
            (y_values[j] - y_values[i]) / (x_values[j] - x_values[i])
            for i in range(len(x_values))
            for j in range(i + 1, len(x_values))
            if x_values[j] != x_values[i]
        ]

        if not slopes:
            raise ValueError("Sen's slope requires distinct timestamps.")

        return float(median(slopes))

    @staticmethod
    def _mann_kendall(values: list[float]) -> tuple[float, float]:
        count = len(values)
        score = 0

        for i in range(count - 1):
            for j in range(i + 1, count):
                difference = values[j] - values[i]
                score += (difference > 0.0) - (difference < 0.0)

        tie_sizes = Counter(values).values()
        tie_correction = sum(size * (size - 1) * (2 * size + 5) for size in tie_sizes if size > 1)

        variance = (count * (count - 1) * (2 * count + 5) - tie_correction) / 18.0

        denominator = count * (count - 1) / 2
        tau = score / denominator

        if variance == 0.0 or score == 0:
            return tau, 1.0

        if score > 0:
            z_score = (score - 1.0) / sqrt(variance)
        else:
            z_score = (score + 1.0) / sqrt(variance)

        p_value = erfc(abs(z_score) / sqrt(2.0))
        return tau, min(1.0, max(0.0, p_value))

    @staticmethod
    def _classify_strength(absolute_tau: float) -> TrendStrength:
        if absolute_tau < 0.1:
            return TrendStrength.VERY_WEAK
        if absolute_tau < 0.3:
            return TrendStrength.WEAK
        if absolute_tau < 0.5:
            return TrendStrength.MODERATE
        if absolute_tau < 0.7:
            return TrendStrength.STRONG
        return TrendStrength.VERY_STRONG
