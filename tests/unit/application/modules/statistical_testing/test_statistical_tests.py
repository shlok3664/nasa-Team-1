"""Tests for statistical test algorithms."""

import pytest

from earth_twin_engine.application.modules.statistical_testing import (
    IncompatibleStatisticalSamplesError,
    InsufficientStatisticalDataError,
    MannKendallTest,
    OneSampleTTest,
    WelchTTest,
)


def test_mann_kendall_detects_increasing_trend(make_series) -> None:
    series = make_series(
        "increasing_temperature",
        [10.0, 12.0, 14.0, 16.0, 18.0, 20.0],
    )

    result = MannKendallTest().run((series,), 0.05)

    assert result.significant is True
    assert result.estimate == pytest.approx(1.0)
    assert result.statistic > 0.0
    assert result.p_value < 0.05
    assert result.valid_observation_counts == (6,)


def test_mann_kendall_detects_decreasing_trend(make_series) -> None:
    series = make_series(
        "decreasing_temperature",
        [20.0, 18.0, 16.0, 14.0, 12.0, 10.0],
    )

    result = MannKendallTest().run((series,), 0.05)

    assert result.significant is True
    assert result.estimate == pytest.approx(-1.0)
    assert result.statistic < 0.0


def test_mann_kendall_handles_tied_values(make_series) -> None:
    series = make_series(
        "tied_temperature",
        [10.0, 10.0, 12.0, 12.0, 14.0, 14.0],
    )

    result = MannKendallTest().run((series,), 0.05)

    assert result.estimate > 0.0
    assert result.p_value < 0.05


def test_mann_kendall_handles_constant_values(make_series) -> None:
    series = make_series(
        "constant_temperature",
        [15.0, 15.0, 15.0, 15.0],
    )

    result = MannKendallTest().run((series,), 0.05)

    assert result.statistic == pytest.approx(0.0)
    assert result.estimate == pytest.approx(0.0)
    assert result.p_value == pytest.approx(1.0)
    assert result.significant is False


def test_mann_kendall_ignores_missing_values(make_series) -> None:
    series = make_series(
        "partially_missing_temperature",
        [10.0, None, 12.0, 14.0, None, 16.0],
    )

    result = MannKendallTest().run((series,), 0.05)

    assert result.sample_sizes == (6,)
    assert result.valid_observation_counts == (4,)
    assert result.missing_observation_counts == (2,)
    assert result.estimate == pytest.approx(1.0)


def test_mann_kendall_rejects_insufficient_data(make_series) -> None:
    series = make_series("short_temperature", [10.0, None, 12.0])

    with pytest.raises(InsufficientStatisticalDataError):
        MannKendallTest().run((series,), 0.05)


def test_one_sample_t_test_detects_mean_difference(make_series) -> None:
    series = make_series(
        "sample_temperature",
        [2.0, 4.0, 6.0, 8.0, 10.0],
    )

    result = OneSampleTTest().run(
        (series,),
        significance_level=0.05,
        reference_value=0.0,
    )

    assert result.significant is True
    assert result.estimate == pytest.approx(6.0)
    assert result.statistic == pytest.approx(4.242640687)
    assert result.degrees_of_freedom == pytest.approx(4.0)
    assert result.p_value < 0.05
    assert result.confidence_interval is not None

    lower, upper = result.confidence_interval
    assert lower > 0.0
    assert upper > lower


def test_one_sample_t_test_ignores_missing_values(make_series) -> None:
    series = make_series(
        "partially_missing_sample",
        [2.0, None, 4.0, 6.0, 8.0],
    )

    result = OneSampleTTest().run(
        (series,),
        significance_level=0.05,
        reference_value=0.0,
    )

    assert result.sample_sizes == (5,)
    assert result.valid_observation_counts == (4,)
    assert result.missing_observation_counts == (1,)


def test_one_sample_t_test_requires_reference_value(make_series) -> None:
    series = make_series("reference_sample", [2.0, 4.0, 6.0])

    with pytest.raises(ValueError, match="reference_value"):
        OneSampleTTest().run((series,), 0.05)


def test_one_sample_t_test_rejects_zero_variance(make_series) -> None:
    series = make_series("zero_variance_sample", [5.0, 5.0, 5.0])

    with pytest.raises(InsufficientStatisticalDataError):
        OneSampleTTest().run((series,), 0.05, reference_value=2.0)


def test_welch_t_test_detects_difference_between_samples(make_series) -> None:
    first = make_series("region_one_temperature", [2.0, 3.0, 4.0, 5.0, 6.0])
    second = make_series("region_two_temperature", [8.0, 9.0, 10.0, 11.0, 12.0])

    result = WelchTTest().run((first, second), 0.05)

    assert result.significant is True
    assert result.estimate == pytest.approx(-6.0)
    assert result.statistic < 0.0
    assert result.degrees_of_freedom is not None
    assert result.confidence_interval is not None

    lower, upper = result.confidence_interval
    assert upper < 0.0
    assert lower < upper


def test_welch_t_test_ignores_missing_values(make_series) -> None:
    first = make_series("first_sample", [2.0, None, 4.0, 6.0])
    second = make_series("second_sample", [8.0, 10.0, None, 12.0])

    result = WelchTTest().run((first, second), 0.05)

    assert result.valid_observation_counts == (3, 3)
    assert result.missing_observation_counts == (1, 1)


def test_welch_t_test_rejects_different_variables(
    make_series,
    variable,
) -> None:
    from earth_twin_engine.domain.variables import EarthVariable, VariableMetadata

    first = make_series("first_variable_sample", [2.0, 3.0, 4.0])
    second_variable = EarthVariable(
        variable_id="precipitation",
        name="Precipitation",
        description="Precipitation amount.",
        category=variable.category,
        metadata=VariableMetadata(
            unit="mm",
            temporal_resolutions=variable.metadata.temporal_resolutions,
        ),
    )

    from dataclasses import replace

    second = replace(second_variable)
    assert second.variable_id != first.variable.variable_id

    second_series = make_series("second_variable_sample", [5.0, 6.0, 7.0])
    second_series = replace(second_series, variable=second)

    with pytest.raises(IncompatibleStatisticalSamplesError):
        WelchTTest().run((first, second_series), 0.05)


def test_welch_t_test_requires_two_samples(make_series) -> None:
    series = make_series("single_sample", [2.0, 3.0, 4.0])

    with pytest.raises(IncompatibleStatisticalSamplesError):
        WelchTTest().run((series,), 0.05)


def test_welch_t_test_rejects_identical_series(make_series) -> None:
    series = make_series("same_sample", [2.0, 3.0, 4.0])

    with pytest.raises(IncompatibleStatisticalSamplesError):
        WelchTTest().run((series, series), 0.05)
