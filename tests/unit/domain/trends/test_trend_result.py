"""Tests for complete scientific trend results."""

import pytest

from earth_twin_engine.domain.trends import (
    ConfidenceInterval,
    SignificanceResult,
    StatisticalTestResult,
    TrendDirection,
    TrendResult,
    TrendSlope,
)


def create_trend(**overrides: object) -> TrendResult:
    values: dict[str, object] = {
        "variable": None,
        "region": None,
        "temporal_range": None,
        "slope": TrendSlope(0.25, "K/year"),
        "direction": TrendDirection.INCREASING,
        "sample_count": 20,
    }

    values.update(overrides)

    return TrendResult(**values)  # type: ignore[arg-type]


def test_create_valid_trend_result(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    result = create_trend(
        variable=trend_variable,
        region=trend_region,
        temporal_range=trend_range,
    )

    assert result.direction is TrendDirection.INCREASING
    assert result.slope.value == 0.25
    assert result.sample_count == 20


def test_allow_optional_statistical_evidence_to_be_missing(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    result = create_trend(
        variable=trend_variable,
        region=trend_region,
        temporal_range=trend_range,
    )

    assert result.confidence_interval is None
    assert result.statistical_test is None
    assert result.significance is None


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("variable", None, "EarthVariable"),
        ("region", None, "GeographicRegion"),
        ("temporal_range", None, "TemporalRange"),
        ("slope", None, "TrendSlope"),
        ("direction", "increasing", "TrendDirection"),
    ],
)
def test_reject_invalid_contract_types(
    trend_variable,
    trend_region,
    trend_range,
    field: str,
    value: object,
    expected_error: str,
) -> None:
    overrides: dict[str, object] = {
        "variable": trend_variable,
        "region": trend_region,
        "temporal_range": trend_range,
    }
    overrides[field] = value

    with pytest.raises(TypeError, match=expected_error):
        create_trend(**overrides)


@pytest.mark.parametrize("sample_count", [0, 1, -1])
def test_reject_insufficient_sample_count(
    trend_variable,
    trend_region,
    trend_range,
    sample_count: int,
) -> None:
    with pytest.raises(ValueError, match="at least 2"):
        create_trend(
            variable=trend_variable,
            region=trend_region,
            temporal_range=trend_range,
            sample_count=sample_count,
        )


def test_reject_boolean_sample_count(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    with pytest.raises(TypeError, match="integer"):
        create_trend(
            variable=trend_variable,
            region=trend_region,
            temporal_range=trend_range,
            sample_count=True,
        )


def test_reject_increasing_trend_with_negative_slope(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    with pytest.raises(ValueError, match="positive slope"):
        create_trend(
            variable=trend_variable,
            region=trend_region,
            temporal_range=trend_range,
            slope=TrendSlope(-0.25, "K/year"),
        )


def test_reject_decreasing_trend_with_positive_slope(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    with pytest.raises(ValueError, match="negative slope"):
        create_trend(
            variable=trend_variable,
            region=trend_region,
            temporal_range=trend_range,
            slope=TrendSlope(0.25, "K/year"),
            direction=TrendDirection.DECREASING,
        )


def test_reject_stable_trend_with_nonzero_slope(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    with pytest.raises(ValueError, match="zero slope"):
        create_trend(
            variable=trend_variable,
            region=trend_region,
            temporal_range=trend_range,
            direction=TrendDirection.STABLE,
        )


def test_allow_stable_trend_with_zero_slope(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    result = create_trend(
        variable=trend_variable,
        region=trend_region,
        temporal_range=trend_range,
        slope=TrendSlope(0, "K/year"),
        direction=TrendDirection.STABLE,
    )

    assert result.direction is TrendDirection.STABLE


def test_allow_undetermined_direction(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    result = create_trend(
        variable=trend_variable,
        region=trend_region,
        temporal_range=trend_range,
        direction=TrendDirection.UNDETERMINED,
    )

    assert result.direction is TrendDirection.UNDETERMINED


def test_reject_invalid_confidence_interval(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    with pytest.raises(TypeError, match="ConfidenceInterval"):
        create_trend(
            variable=trend_variable,
            region=trend_region,
            temporal_range=trend_range,
            confidence_interval="invalid",
        )


def test_reject_invalid_statistical_test(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    with pytest.raises(TypeError, match="StatisticalTestResult"):
        create_trend(
            variable=trend_variable,
            region=trend_region,
            temporal_range=trend_range,
            statistical_test="invalid",
        )


def test_reject_invalid_significance(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    with pytest.raises(TypeError, match="SignificanceResult"):
        create_trend(
            variable=trend_variable,
            region=trend_region,
            temporal_range=trend_range,
            significance="invalid",
        )


def test_reject_mismatched_significance_evidence(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    test_result = StatisticalTestResult(
        test_name="Mann-Kendall",
        statistic_name="S",
        statistic_value=15,
        sample_count=20,
        significance=SignificanceResult(0.01),
    )

    with pytest.raises(ValueError, match="must match"):
        create_trend(
            variable=trend_variable,
            region=trend_region,
            temporal_range=trend_range,
            statistical_test=test_result,
            significance=SignificanceResult(0.10),
        )


def test_accept_matching_statistical_evidence(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    significance = SignificanceResult(0.01)
    test_result = StatisticalTestResult(
        test_name="Mann-Kendall",
        statistic_name="S",
        statistic_value=15,
        sample_count=20,
        significance=significance,
    )

    result = create_trend(
        variable=trend_variable,
        region=trend_region,
        temporal_range=trend_range,
        statistical_test=test_result,
        significance=significance,
        confidence_interval=ConfidenceInterval(0.1, 0.4, 0.95),
    )

    assert result.significance.is_significant
    assert result.confidence_interval.width == pytest.approx(0.3)


def test_trend_result_is_immutable(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    result = create_trend(
        variable=trend_variable,
        region=trend_region,
        temporal_range=trend_range,
    )

    with pytest.raises(AttributeError):
        result.sample_count = 30  # type: ignore[misc]
