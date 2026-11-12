"""Statistical test implementations and numerical distribution utilities."""

from collections import Counter
from datetime import UTC, datetime
from math import erfc, exp, isfinite, lgamma, log, sqrt
from statistics import fmean, stdev
from typing import Protocol

from earth_twin_engine.domain.time_series import TimeSeries

from .errors import (
    IncompatibleStatisticalSamplesError,
    InsufficientStatisticalDataError,
)
from .statistical_test_method import StatisticalTestMethod
from .statistical_test_result import StatisticalTestResult


class StatisticalTest(Protocol):
    """Contract implemented by every statistical test."""

    @property
    def method(self) -> StatisticalTestMethod: ...

    def run(
        self,
        series: tuple[TimeSeries, ...],
        significance_level: float,
        reference_value: float | None = None,
    ) -> StatisticalTestResult: ...


def _valid_values(series: TimeSeries) -> list[float]:
    return [float(point.value) for point in series.points if point.value is not None]


def _validate_significance_level(value: float) -> None:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not isfinite(value)
        or not 0.0 < value < 1.0
    ):
        raise ValueError("significance_level must be finite and between 0 and 1.")


def _validate_single_sample(series: tuple[TimeSeries, ...]) -> TimeSeries:
    if len(series) != 1:
        raise IncompatibleStatisticalSamplesError("This test requires exactly one time series.")
    return series[0]


def _validate_two_samples(
    series: tuple[TimeSeries, ...],
) -> tuple[TimeSeries, TimeSeries]:
    if len(series) != 2:
        raise IncompatibleStatisticalSamplesError("This test requires exactly two time series.")

    first, second = series

    if first.variable.variable_id != second.variable.variable_id:
        raise IncompatibleStatisticalSamplesError(
            "Both series must represent the same Earth variable."
        )

    if first.variable.metadata.unit != second.variable.metadata.unit:
        raise IncompatibleStatisticalSamplesError("Both series must use the same measurement unit.")

    if first.series_id == second.series_id:
        raise IncompatibleStatisticalSamplesError("The two samples must have different series IDs.")

    return first, second


def _regularized_incomplete_beta(
    x: float,
    a: float,
    b: float,
) -> float:
    """Evaluate the regularized incomplete beta function."""

    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0

    log_factor = lgamma(a + b) - lgamma(a) - lgamma(b) + a * log(x) + b * log(1.0 - x)
    factor = 0.0 if log_factor < -745.0 else exp(log_factor)

    if x < (a + 1.0) / (a + b + 2.0):
        return factor * _beta_continued_fraction(a, b, x) / a

    return 1.0 - (factor * _beta_continued_fraction(b, a, 1.0 - x) / b)


def _beta_continued_fraction(a: float, b: float, x: float) -> float:
    """Evaluate the incomplete beta continued fraction."""

    maximum_iterations = 200
    epsilon = 3.0e-14
    minimum = 1.0e-300

    qab = a + b
    qap = a + 1.0
    qam = a - 1.0

    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < minimum:
        d = minimum

    d = 1.0 / d
    result = d

    for iteration in range(1, maximum_iterations + 1):
        m2 = 2 * iteration
        coefficient = iteration * (b - iteration) * x / ((qam + m2) * (a + m2))

        d = 1.0 + coefficient * d
        if abs(d) < minimum:
            d = minimum

        c = 1.0 + coefficient / c
        if abs(c) < minimum:
            c = minimum

        d = 1.0 / d
        result *= d * c

        coefficient = -(a + iteration) * (qab + iteration) * x / ((a + m2) * (qap + m2))

        d = 1.0 + coefficient * d
        if abs(d) < minimum:
            d = minimum

        c = 1.0 + coefficient / c
        if abs(c) < minimum:
            c = minimum

        d = 1.0 / d
        delta = d * c
        result *= delta

        if abs(delta - 1.0) < epsilon:
            return result

    raise ArithmeticError("Incomplete beta continued fraction did not converge.")


def _student_t_cdf(value: float, degrees_of_freedom: float) -> float:
    """Calculate the Student's t cumulative distribution."""

    x = degrees_of_freedom / (degrees_of_freedom + value * value)
    beta_value = _regularized_incomplete_beta(
        x,
        degrees_of_freedom / 2.0,
        0.5,
    )

    if value >= 0.0:
        return 1.0 - 0.5 * beta_value

    return 0.5 * beta_value


def _student_t_quantile(probability: float, degrees_of_freedom: float) -> float:
    """Numerically invert the Student's t cumulative distribution."""

    if not 0.0 < probability < 1.0:
        raise ValueError("probability must be between 0 and 1.")

    if probability == 0.5:
        return 0.0

    lower = -1.0
    upper = 1.0

    while _student_t_cdf(lower, degrees_of_freedom) > probability:
        lower *= 2.0

    while _student_t_cdf(upper, degrees_of_freedom) < probability:
        upper *= 2.0

    for _ in range(120):
        midpoint = (lower + upper) / 2.0
        if _student_t_cdf(midpoint, degrees_of_freedom) < probability:
            lower = midpoint
        else:
            upper = midpoint

    return (lower + upper) / 2.0


def _make_result(
    *,
    method: StatisticalTestMethod,
    series: tuple[TimeSeries, ...],
    values: tuple[list[float], ...],
    statistic: float,
    p_value: float,
    significance_level: float,
    estimate: float,
    degrees_of_freedom: float | None,
    confidence_interval: tuple[float, float] | None,
    assumptions: tuple[str, ...],
    warnings: tuple[str, ...] = (),
) -> StatisticalTestResult:
    sample_sizes = tuple(len(item.points) for item in series)
    valid_counts = tuple(len(item) for item in values)

    return StatisticalTestResult(
        method=method,
        series_ids=tuple(item.series_id for item in series),
        statistic=statistic,
        p_value=min(1.0, max(0.0, p_value)),
        significance_level=significance_level,
        significant=p_value < significance_level,
        estimate=estimate,
        degrees_of_freedom=degrees_of_freedom,
        sample_sizes=sample_sizes,
        valid_observation_counts=valid_counts,
        missing_observation_counts=tuple(
            sample - valid for sample, valid in zip(sample_sizes, valid_counts, strict=True)
        ),
        confidence_interval=confidence_interval,
        assumptions=assumptions,
        warnings=warnings,
        analyzed_at=datetime.now(UTC),
    )


class MannKendallTest:
    """Non-parametric test for a monotonic trend."""

    @property
    def method(self) -> StatisticalTestMethod:
        return StatisticalTestMethod.MANN_KENDALL

    def run(
        self,
        series: tuple[TimeSeries, ...],
        significance_level: float,
        reference_value: float | None = None,
    ) -> StatisticalTestResult:
        _validate_significance_level(significance_level)
        item = _validate_single_sample(series)

        if reference_value is not None:
            raise ValueError("Mann-Kendall does not accept a reference value.")

        values = _valid_values(item)
        count = len(values)

        if count < 3:
            raise InsufficientStatisticalDataError(
                "Mann-Kendall requires at least three valid observations."
            )

        score = sum(
            (values[j] > values[i]) - (values[j] < values[i])
            for i in range(count - 1)
            for j in range(i + 1, count)
        )

        tie_correction = sum(
            size * (size - 1) * (2 * size + 5) for size in Counter(values).values() if size > 1
        )
        variance = (count * (count - 1) * (2 * count + 5) - tie_correction) / 18.0

        pair_count = count * (count - 1) / 2.0
        tau = score / pair_count

        if variance <= 0.0 or score == 0:
            z_score = 0.0
            p_value = 1.0
        elif score > 0:
            z_score = (score - 1.0) / sqrt(variance)
            p_value = erfc(abs(z_score) / sqrt(2.0))
        else:
            z_score = (score + 1.0) / sqrt(variance)
            p_value = erfc(abs(z_score) / sqrt(2.0))

        warnings = (
            ("The asymptotic normal approximation may be inaccurate for small samples.",)
            if count < 10
            else ()
        )

        return _make_result(
            method=self.method,
            series=series,
            values=(values,),
            statistic=z_score,
            p_value=p_value,
            significance_level=significance_level,
            estimate=tau,
            degrees_of_freedom=None,
            confidence_interval=None,
            assumptions=(
                "Observations are ordered in time.",
                "Observations are independent under the null hypothesis.",
                "The test detects monotonic association, not causation.",
            ),
            warnings=warnings,
        )


class OneSampleTTest:
    """Two-sided one-sample Student's t-test."""

    @property
    def method(self) -> StatisticalTestMethod:
        return StatisticalTestMethod.ONE_SAMPLE_T

    def run(
        self,
        series: tuple[TimeSeries, ...],
        significance_level: float,
        reference_value: float | None = None,
    ) -> StatisticalTestResult:
        _validate_significance_level(significance_level)
        item = _validate_single_sample(series)

        if (
            not isinstance(reference_value, (int, float))
            or isinstance(reference_value, bool)
            or not isfinite(reference_value)
        ):
            raise ValueError("A finite numeric reference_value is required.")

        values = _valid_values(item)
        count = len(values)

        if count < 2:
            raise InsufficientStatisticalDataError(
                "One-sample t-test requires at least two valid observations."
            )

        mean = fmean(values)
        standard_deviation = stdev(values)
        degrees_of_freedom = float(count - 1)

        if standard_deviation == 0.0:
            raise InsufficientStatisticalDataError(
                "One-sample t-test requires non-zero sample variance."
            )

        standard_error = standard_deviation / sqrt(count)
        difference = mean - float(reference_value)
        statistic = difference / standard_error
        p_value = 2.0 * (1.0 - _student_t_cdf(abs(statistic), degrees_of_freedom))

        critical_value = _student_t_quantile(
            1.0 - significance_level / 2.0,
            degrees_of_freedom,
        )
        confidence_interval = (
            difference - critical_value * standard_error,
            difference + critical_value * standard_error,
        )

        return _make_result(
            method=self.method,
            series=series,
            values=(values,),
            statistic=statistic,
            p_value=p_value,
            significance_level=significance_level,
            estimate=difference,
            degrees_of_freedom=degrees_of_freedom,
            confidence_interval=confidence_interval,
            assumptions=(
                "Observations are independent.",
                "The sample is drawn from a population with finite variance.",
                "The population distribution is approximately normal, "
                "especially for small samples.",
            ),
            warnings=(
                ("The sample contains fewer than 30 valid observations.",) if count < 30 else ()
            ),
        )


class WelchTTest:
    """Two-sided Welch independent-samples t-test."""

    @property
    def method(self) -> StatisticalTestMethod:
        return StatisticalTestMethod.WELCH_T

    def run(
        self,
        series: tuple[TimeSeries, ...],
        significance_level: float,
        reference_value: float | None = None,
    ) -> StatisticalTestResult:
        _validate_significance_level(significance_level)
        first, second = _validate_two_samples(series)

        if reference_value is not None:
            raise ValueError("Welch's t-test does not accept a reference value.")

        first_values = _valid_values(first)
        second_values = _valid_values(second)

        if len(first_values) < 2 or len(second_values) < 2:
            raise InsufficientStatisticalDataError(
                "Welch's t-test requires at least two valid observations per sample."
            )

        first_variance = stdev(first_values) ** 2
        second_variance = stdev(second_values) ** 2

        first_component = first_variance / len(first_values)
        second_component = second_variance / len(second_values)
        standard_error_squared = first_component + second_component

        if standard_error_squared == 0.0:
            raise InsufficientStatisticalDataError(
                "Welch's t-test requires non-zero combined sample variance."
            )

        standard_error = sqrt(standard_error_squared)
        difference = fmean(first_values) - fmean(second_values)
        statistic = difference / standard_error

        degrees_of_freedom = standard_error_squared**2 / (
            first_component**2 / (len(first_values) - 1)
            + second_component**2 / (len(second_values) - 1)
        )

        p_value = 2.0 * (1.0 - _student_t_cdf(abs(statistic), degrees_of_freedom))

        critical_value = _student_t_quantile(
            1.0 - significance_level / 2.0,
            degrees_of_freedom,
        )
        confidence_interval = (
            difference - critical_value * standard_error,
            difference + critical_value * standard_error,
        )

        return _make_result(
            method=self.method,
            series=series,
            values=(first_values, second_values),
            statistic=statistic,
            p_value=p_value,
            significance_level=significance_level,
            estimate=difference,
            degrees_of_freedom=degrees_of_freedom,
            confidence_interval=confidence_interval,
            assumptions=(
                "The two samples are independent.",
                "Each population is approximately normal, especially for small samples.",
                "The two populations are not assumed to have equal variances.",
            ),
            warnings=(
                ("The first sample contains fewer than 30 valid observations.",)
                if len(first_values) < 30
                else ()
            )
            + (
                ("The second sample contains fewer than 30 valid observations.",)
                if len(second_values) < 30
                else ()
            ),
        )
