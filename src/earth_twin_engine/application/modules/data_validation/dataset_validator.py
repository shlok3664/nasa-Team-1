"""Validates scientific datasets and their associated time-series observations."""

from math import isfinite

from earth_twin_engine.domain.datasets.dataset import Dataset
from earth_twin_engine.domain.time_series.time_series import TimeSeries

from .validation_issue import ValidationIssue
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity


class DatasetValidator:
    """Checks consistency between a dataset request and its observations."""

    def __init__(self, max_missing_fraction: float = 0.0) -> None:
        if isinstance(max_missing_fraction, bool) or not isinstance(
            max_missing_fraction, (int, float)
        ):
            raise TypeError("max_missing_fraction must be a number")

        if not isfinite(max_missing_fraction):
            raise ValueError("max_missing_fraction must be finite")

        if not 0.0 <= max_missing_fraction <= 1.0:
            raise ValueError("max_missing_fraction must be between 0.0 and 1.0")

        self._max_missing_fraction = float(max_missing_fraction)

    @property
    def max_missing_fraction(self) -> float:
        """Return the configured maximum missing-observation fraction."""

        return self._max_missing_fraction

    def validate(
        self,
        dataset: Dataset,
        time_series: tuple[TimeSeries, ...],
    ) -> ValidationResult:
        """Validate time-series observations against their dataset request."""

        if not isinstance(dataset, Dataset):
            raise TypeError("dataset must be a Dataset")

        if not isinstance(time_series, tuple):
            raise TypeError("time_series must be a tuple")

        if not all(isinstance(series, TimeSeries) for series in time_series):
            raise TypeError("time_series must contain only TimeSeries values")

        issues: list[ValidationIssue] = []
        observation_count = 0
        valid_observation_count = 0
        missing_observation_count = 0

        request = dataset.request
        expected_variable_id = request.variable.variable_id
        expected_resolution = request.temporal_resolution
        region_boundary = request.region.boundary
        temporal_range = request.temporal_range

        def add_issue(
            code: str,
            message: str,
            severity: ValidationSeverity,
            series_id: str | None = None,
            observation_index: int | None = None,
        ) -> None:
            issues.append(
                ValidationIssue(
                    code=code,
                    message=message,
                    severity=severity,
                    series_id=series_id,
                    observation_index=observation_index,
                )
            )

        if not time_series:
            add_issue(
                code="NO_TIME_SERIES",
                message="The dataset contains no associated time series.",
                severity=ValidationSeverity.ERROR,
            )

        allowed_source_ids = request.variable.metadata.source_ids
        actual_source_id = dataset.provenance.source.source_id

        if allowed_source_ids and actual_source_id not in allowed_source_ids:
            add_issue(
                code="SOURCE_NOT_ALLOWED_FOR_VARIABLE",
                message=(
                    f"Source '{actual_source_id}' is not listed as a supported "
                    f"source for variable '{expected_variable_id}'."
                ),
                severity=ValidationSeverity.ERROR,
            )

        seen_series_ids: set[str] = set()

        for series in time_series:
            series_id = series.series_id
            points = series.points

            if series_id in seen_series_ids:
                add_issue(
                    code="DUPLICATE_SERIES_ID",
                    message=f"Time-series ID '{series_id}' occurs more than once.",
                    severity=ValidationSeverity.ERROR,
                    series_id=series_id,
                )
            else:
                seen_series_ids.add(series_id)

            if series.variable.variable_id != expected_variable_id:
                add_issue(
                    code="VARIABLE_MISMATCH",
                    message=(
                        f"Time series '{series_id}' uses variable "
                        f"'{series.variable.variable_id}' instead of "
                        f"'{expected_variable_id}'."
                    ),
                    severity=ValidationSeverity.ERROR,
                    series_id=series_id,
                )

            if series.temporal_resolution is not expected_resolution:
                add_issue(
                    code="TEMPORAL_RESOLUTION_MISMATCH",
                    message=(
                        f"Time series '{series_id}' uses resolution "
                        f"'{series.temporal_resolution.value}' instead of "
                        f"'{expected_resolution.value}'."
                    ),
                    severity=ValidationSeverity.ERROR,
                    series_id=series_id,
                )

            if not region_boundary.contains(series.location):
                add_issue(
                    code="LOCATION_OUTSIDE_REGION",
                    message=(
                        f"Time series '{series_id}' is located outside "
                        f"the requested geographic region."
                    ),
                    severity=ValidationSeverity.ERROR,
                    series_id=series_id,
                )

            series_missing_count = 0

            for observation_index, point in enumerate(points):
                observation_count += 1

                if not temporal_range.contains(point.timestamp):
                    add_issue(
                        code="OBSERVATION_OUTSIDE_TEMPORAL_RANGE",
                        message=(
                            f"Observation timestamp '{point.timestamp.isoformat()}' "
                            "falls outside the requested temporal range."
                        ),
                        severity=ValidationSeverity.ERROR,
                        series_id=series_id,
                        observation_index=observation_index,
                    )

                if point.value is None:
                    missing_observation_count += 1
                    series_missing_count += 1
                else:
                    valid_observation_count += 1

            if points and series_missing_count == len(points):
                add_issue(
                    code="ALL_OBSERVATIONS_MISSING",
                    message=(
                        f"Every observation in time series '{series_id}' has a missing value."
                    ),
                    severity=ValidationSeverity.ERROR,
                    series_id=series_id,
                )
            elif points:
                missing_fraction = series_missing_count / len(points)

                if missing_fraction > self._max_missing_fraction:
                    add_issue(
                        code="MISSING_OBSERVATIONS",
                        message=(
                            f"Time series '{series_id}' has "
                            f"{series_missing_count} missing observations out of "
                            f"{len(points)} "
                            f"({missing_fraction:.1%}), exceeding the configured "
                            f"threshold of {self._max_missing_fraction:.1%}."
                        ),
                        severity=ValidationSeverity.WARNING,
                        series_id=series_id,
                    )

        return ValidationResult(
            dataset_id=dataset.dataset_id,
            issues=tuple(issues),
            checked_series_count=len(time_series),
            observation_count=observation_count,
            valid_observation_count=valid_observation_count,
            missing_observation_count=missing_observation_count,
        )
