"""Tests for scientific dataset validation."""

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from earth_twin_engine.application.modules.data_validation import (
    DatasetValidator,
    ValidationSeverity,
)
from earth_twin_engine.domain.geography import SpatialCoordinate
from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import TimeSeriesPoint
from earth_twin_engine.domain.variables import (
    EarthVariable,
    VariableCategory,
    VariableMetadata,
)


def issue_codes(result) -> set[str]:
    """Return all issue codes in a validation result."""

    return {issue.code for issue in result.issues}


def test_valid_dataset_passes_validation(dataset, valid_time_series_collection) -> None:
    validator = DatasetValidator()

    result = validator.validate(dataset, valid_time_series_collection)

    assert result.dataset_id == dataset.dataset_id
    assert result.is_valid
    assert not result.has_warnings
    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.checked_series_count == 1
    assert result.observation_count == 3
    assert result.valid_observation_count == 3
    assert result.missing_observation_count == 0
    assert result.issues == ()


def test_empty_time_series_collection_is_an_error(dataset) -> None:
    result = DatasetValidator().validate(dataset, ())

    assert not result.is_valid
    assert "NO_TIME_SERIES" in issue_codes(result)
    assert result.checked_series_count == 0
    assert result.observation_count == 0


def test_wrong_variable_is_an_error(
    dataset,
    valid_time_series,
) -> None:
    other_variable = EarthVariable(
        variable_id="precipitation",
        name="Precipitation",
        description="Daily precipitation.",
        category=VariableCategory.HYDROLOGY,
        metadata=VariableMetadata(
            unit="mm",
            temporal_resolutions=(TemporalResolution.DAILY,),
        ),
    )

    invalid_series = replace(
        valid_time_series,
        variable=other_variable,
    )

    result = DatasetValidator().validate(dataset, (invalid_series,))

    assert not result.is_valid
    assert "VARIABLE_MISMATCH" in issue_codes(result)


def test_wrong_temporal_resolution_is_an_error(
    dataset,
    valid_time_series,
) -> None:
    hourly_series = replace(
        valid_time_series,
        temporal_resolution=TemporalResolution.HOURLY,
    )

    result = DatasetValidator().validate(dataset, (hourly_series,))

    assert not result.is_valid
    assert "TEMPORAL_RESOLUTION_MISMATCH" in issue_codes(result)


def test_location_outside_requested_region_is_an_error(
    dataset,
    valid_time_series,
) -> None:
    outside_series = replace(
        valid_time_series,
        location=SpatialCoordinate(
            latitude=51.5074,
            longitude=-0.1278,
        ),
    )

    result = DatasetValidator().validate(dataset, (outside_series,))

    assert not result.is_valid
    assert "LOCATION_OUTSIDE_REGION" in issue_codes(result)


def test_observation_at_exclusive_end_is_outside_temporal_range(
    dataset,
    valid_time_series,
) -> None:
    outside_series = replace(
        valid_time_series,
        points=(
            TimeSeriesPoint(
                timestamp=datetime(2021, 1, 1, tzinfo=UTC),
                value=285.4,
            ),
        ),
    )

    result = DatasetValidator().validate(dataset, (outside_series,))

    assert not result.is_valid

    issue = next(
        issue for issue in result.issues if issue.code == "OBSERVATION_OUTSIDE_TEMPORAL_RANGE"
    )

    assert issue.series_id == outside_series.series_id
    assert issue.observation_index == 0


def test_missing_observations_produce_warning_by_default(
    dataset,
    valid_time_series,
) -> None:
    series_with_missing_value = replace(
        valid_time_series,
        points=(
            TimeSeriesPoint(
                timestamp=datetime(2020, 1, 1, tzinfo=UTC),
                value=285.4,
            ),
            TimeSeriesPoint(
                timestamp=datetime(2020, 1, 2, tzinfo=UTC),
                value=None,
            ),
            TimeSeriesPoint(
                timestamp=datetime(2020, 1, 3, tzinfo=UTC),
                value=284.9,
            ),
        ),
    )

    result = DatasetValidator().validate(
        dataset,
        (series_with_missing_value,),
    )

    assert result.is_valid
    assert result.has_warnings
    assert result.warning_count == 1
    assert result.observation_count == 3
    assert result.valid_observation_count == 2
    assert result.missing_observation_count == 1
    assert "MISSING_OBSERVATIONS" in issue_codes(result)


def test_missing_fraction_threshold_can_allow_missing_observations(
    dataset,
    valid_time_series,
) -> None:
    series_with_missing_value = replace(
        valid_time_series,
        points=(
            TimeSeriesPoint(
                timestamp=datetime(2020, 1, 1, tzinfo=UTC),
                value=285.4,
            ),
            TimeSeriesPoint(
                timestamp=datetime(2020, 1, 2, tzinfo=UTC),
                value=None,
            ),
            TimeSeriesPoint(
                timestamp=datetime(2020, 1, 3, tzinfo=UTC),
                value=284.9,
            ),
        ),
    )

    result = DatasetValidator(max_missing_fraction=0.5).validate(
        dataset,
        (series_with_missing_value,),
    )

    assert result.is_valid
    assert not result.has_warnings
    assert "MISSING_OBSERVATIONS" not in issue_codes(result)


def test_all_missing_observations_are_an_error(
    dataset,
    valid_time_series,
) -> None:
    all_missing_series = replace(
        valid_time_series,
        points=(
            TimeSeriesPoint(
                timestamp=datetime(2020, 1, 1, tzinfo=UTC),
                value=None,
            ),
            TimeSeriesPoint(
                timestamp=datetime(2020, 1, 2, tzinfo=UTC),
                value=None,
            ),
        ),
    )

    result = DatasetValidator().validate(dataset, (all_missing_series,))

    assert not result.is_valid
    assert "ALL_OBSERVATIONS_MISSING" in issue_codes(result)
    assert "MISSING_OBSERVATIONS" not in issue_codes(result)
    assert result.valid_observation_count == 0
    assert result.missing_observation_count == 2


def test_duplicate_series_ids_are_an_error(
    dataset,
    valid_time_series,
) -> None:
    duplicate = replace(
        valid_time_series,
        location=SpatialCoordinate(
            latitude=19.0760,
            longitude=72.8777,
        ),
    )

    result = DatasetValidator().validate(
        dataset,
        (valid_time_series, duplicate),
    )

    assert not result.is_valid
    assert "DUPLICATE_SERIES_ID" in issue_codes(result)
    assert result.checked_series_count == 2
    assert result.observation_count == 6


def test_unsupported_source_for_variable_is_an_error(
    dataset,
    valid_time_series,
) -> None:
    restricted_variable = replace(
        dataset.request.variable,
        metadata=replace(
            dataset.request.variable.metadata,
            source_ids=("another_source",),
        ),
    )

    restricted_request = replace(
        dataset.request,
        variable=restricted_variable,
    )

    restricted_dataset = replace(
        dataset,
        request=restricted_request,
    )

    result = DatasetValidator().validate(
        restricted_dataset,
        (valid_time_series,),
    )

    assert not result.is_valid
    assert "SOURCE_NOT_ALLOWED_FOR_VARIABLE" in issue_codes(result)


@pytest.mark.parametrize(
    "threshold",
    (-0.1, 1.1, float("inf"), float("-inf"), float("nan")),
)
def test_invalid_missing_fraction_threshold_is_rejected(threshold) -> None:
    with pytest.raises(ValueError):
        DatasetValidator(max_missing_fraction=threshold)


def test_boolean_missing_fraction_threshold_is_rejected() -> None:
    with pytest.raises(TypeError):
        DatasetValidator(max_missing_fraction=True)


def test_non_numeric_missing_fraction_threshold_is_rejected() -> None:
    with pytest.raises(TypeError):
        DatasetValidator(max_missing_fraction="0.2")


def test_invalid_dataset_argument_is_rejected(valid_time_series_collection) -> None:
    with pytest.raises(TypeError):
        DatasetValidator().validate(None, valid_time_series_collection)


def test_non_tuple_time_series_argument_is_rejected(dataset) -> None:
    with pytest.raises(TypeError):
        DatasetValidator().validate(dataset, [])


def test_invalid_time_series_collection_member_is_rejected(dataset) -> None:
    with pytest.raises(TypeError):
        DatasetValidator().validate(dataset, ("not-a-time-series",))


def test_validation_result_preserves_issue_severity(
    dataset,
    valid_time_series,
) -> None:
    invalid_series = replace(
        valid_time_series,
        location=SpatialCoordinate(
            latitude=51.5074,
            longitude=-0.1278,
        ),
    )

    result = DatasetValidator().validate(dataset, (invalid_series,))

    location_issue = next(
        issue for issue in result.issues if issue.code == "LOCATION_OUTSIDE_REGION"
    )

    assert location_issue.severity is ValidationSeverity.ERROR
