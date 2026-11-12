"""Tests for statistical trend contracts."""

import pytest

from earth_twin_engine.domain.trends import (
    ConfidenceInterval,
    SignificanceResult,
    StatisticalTestResult,
    TrendSlope,
)


def test_create_valid_trend_slope() -> None:
    slope = TrendSlope(0.25, "K/year")

    assert slope.value == 0.25
    assert slope.unit == "K/year"


def test_reject_non_numeric_slope() -> None:
    with pytest.raises(TypeError, match="numeric"):
        TrendSlope(True, "K/year")


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_reject_non_finite_slope(value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        TrendSlope(value, "K/year")


def test_reject_empty_slope_unit() -> None:
    with pytest.raises(ValueError, match="unit"):
        TrendSlope(0.25, " ")


def test_create_valid_confidence_interval() -> None:
    interval = ConfidenceInterval(
        lower_bound=0.1,
        upper_bound=0.4,
        confidence_level=0.95,
    )

    assert interval.width == pytest.approx(0.3)
    assert interval.contains(0.25)
    assert not interval.contains(0.5)


def test_allow_equal_confidence_interval_bounds() -> None:
    interval = ConfidenceInterval(0.5, 0.5, 0.95)

    assert interval.width == 0


def test_reject_reversed_confidence_interval() -> None:
    with pytest.raises(ValueError, match="lower_bound"):
        ConfidenceInterval(0.5, 0.1, 0.95)


@pytest.mark.parametrize("level", [0, 1, -0.1, 1.1])
def test_reject_invalid_confidence_level(level: float) -> None:
    with pytest.raises(ValueError, match="confidence_level"):
        ConfidenceInterval(0.1, 0.5, level)


def test_reject_non_numeric_confidence_bound() -> None:
    with pytest.raises(TypeError, match="lower_bound"):
        ConfidenceInterval(True, 0.5, 0.95)


def test_reject_non_finite_confidence_bound() -> None:
    with pytest.raises(ValueError, match="finite"):
        ConfidenceInterval(0.1, float("inf"), 0.95)


def test_reject_non_finite_value_in_contains() -> None:
    interval = ConfidenceInterval(0.1, 0.5, 0.95)

    with pytest.raises(ValueError, match="finite"):
        interval.contains(float("nan"))


def test_create_significance_result() -> None:
    result = SignificanceResult(p_value=0.01, alpha=0.05)

    assert result.is_significant


def test_non_significant_result() -> None:
    result = SignificanceResult(p_value=0.08, alpha=0.05)

    assert not result.is_significant


def test_p_value_equal_to_alpha_is_not_significant() -> None:
    result = SignificanceResult(p_value=0.05, alpha=0.05)

    assert not result.is_significant


@pytest.mark.parametrize("p_value", [-0.1, 1.1])
def test_reject_invalid_p_value(p_value: float) -> None:
    with pytest.raises(ValueError, match="p_value"):
        SignificanceResult(p_value=p_value)


@pytest.mark.parametrize("alpha", [0, 1, -0.1, 1.1])
def test_reject_invalid_alpha(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha"):
        SignificanceResult(p_value=0.01, alpha=alpha)


def test_reject_boolean_p_value() -> None:
    with pytest.raises(TypeError, match="p_value"):
        SignificanceResult(p_value=True)


def test_reject_non_finite_significance_value() -> None:
    with pytest.raises(ValueError, match="finite"):
        SignificanceResult(p_value=float("nan"))


def test_create_statistical_test_result() -> None:
    result = StatisticalTestResult(
        test_name="Mann-Kendall",
        statistic_name="S",
        statistic_value=15.0,
        sample_count=20,
        significance=SignificanceResult(0.01),
    )

    assert result.test_name == "Mann-Kendall"
    assert result.sample_count == 20
    assert result.significance.is_significant


def test_reject_empty_statistical_test_name() -> None:
    with pytest.raises(ValueError, match="test_name"):
        StatisticalTestResult(
            "",
            "S",
            15,
            20,
            SignificanceResult(0.01),
        )


def test_reject_invalid_statistic_value() -> None:
    with pytest.raises(TypeError, match="statistic_value"):
        StatisticalTestResult(
            "Mann-Kendall",
            "S",
            True,
            20,
            SignificanceResult(0.01),
        )


def test_reject_non_finite_statistic_value() -> None:
    with pytest.raises(ValueError, match="finite"):
        StatisticalTestResult(
            "Mann-Kendall",
            "S",
            float("inf"),
            20,
            SignificanceResult(0.01),
        )


def test_reject_invalid_sample_count() -> None:
    with pytest.raises(ValueError, match="positive"):
        StatisticalTestResult(
            "Mann-Kendall",
            "S",
            15,
            0,
            SignificanceResult(0.01),
        )


def test_reject_boolean_sample_count() -> None:
    with pytest.raises(TypeError, match="integer"):
        StatisticalTestResult(
            "Mann-Kendall",
            "S",
            15,
            True,
            SignificanceResult(0.01),
        )


def test_reject_invalid_significance_contract() -> None:
    with pytest.raises(TypeError, match="SignificanceResult"):
        StatisticalTestResult(
            "Mann-Kendall",
            "S",
            15,
            20,
            None,  # type: ignore[arg-type]
        )


def test_reject_non_integer_sample_count() -> None:
    with pytest.raises(TypeError, match="integer"):
        StatisticalTestResult(
            "Mann-Kendall",
            "S",
            15,
            2.5,  # type: ignore[arg-type]
            SignificanceResult(0.01),
        )


def test_statistical_contracts_are_immutable() -> None:
    slope = TrendSlope(0.25, "K/year")
    interval = ConfidenceInterval(0.1, 0.4, 0.95)
    significance = SignificanceResult(0.01)
    test_result = StatisticalTestResult(
        "Mann-Kendall",
        "S",
        15,
        20,
        significance,
    )

    with pytest.raises(AttributeError):
        slope.value = 1.0  # type: ignore[misc]

    with pytest.raises(AttributeError):
        interval.confidence_level = 0.90  # type: ignore[misc]

    with pytest.raises(AttributeError):
        significance.alpha = 0.10  # type: ignore[misc]

    with pytest.raises(AttributeError):
        test_result.sample_count = 10  # type: ignore[misc]
