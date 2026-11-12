"""Normalizes scientific datasets and their time-series observations."""

from dataclasses import replace
from datetime import UTC

from earth_twin_engine.domain.datasets import DataProvenance, Dataset
from earth_twin_engine.domain.time_series import TimeSeries, TimeSeriesPoint

from .normalization_error import (
    UnsupportedUnitConversionError,
    VariableMismatchError,
)
from .normalization_result import NormalizationResult
from .unit_conversion_registry import UnitConversionRegistry


class DataNormalizer:
    """Normalizes time-series values and dataset metadata."""

    def __init__(
        self,
        unit_registry: UnitConversionRegistry | None = None,
    ) -> None:
        if unit_registry is not None and not isinstance(
            unit_registry,
            UnitConversionRegistry,
        ):
            raise TypeError("unit_registry must be a UnitConversionRegistry or None.")

        self._unit_registry = (
            unit_registry if unit_registry is not None else UnitConversionRegistry()
        )

    @property
    def unit_registry(self) -> UnitConversionRegistry:
        """Return the unit conversion registry."""
        return self._unit_registry

    def normalize(
        self,
        dataset: Dataset,
        time_series: tuple[TimeSeries, ...],
    ) -> NormalizationResult:
        """Normalize observations to the dataset variable's canonical unit."""
        if not isinstance(dataset, Dataset):
            raise TypeError("dataset must be a Dataset.")

        if not isinstance(time_series, tuple):
            raise TypeError("time_series must be a tuple.")

        if any(not isinstance(series, TimeSeries) for series in time_series):
            raise TypeError("Every item in time_series must be a TimeSeries.")

        target_variable = dataset.request.variable
        target_unit = target_variable.metadata.unit

        normalized_series: list[TimeSeries] = []
        conversion_transformations: list[str] = []

        for series in time_series:
            if series.variable.variable_id != target_variable.variable_id:
                raise VariableMismatchError(
                    f"Series '{series.series_id}' uses variable "
                    f"'{series.variable.variable_id}', but the dataset "
                    f"uses '{target_variable.variable_id}'."
                )

            source_unit = series.variable.metadata.unit

            if not self._unit_registry.supports(source_unit, target_unit):
                raise UnsupportedUnitConversionError(
                    f"No conversion is available from '{source_unit}' "
                    f"to '{target_unit}' for series '{series.series_id}'."
                )

            normalized_points = tuple(
                TimeSeriesPoint(
                    timestamp=point.timestamp.astimezone(UTC),
                    value=(
                        None
                        if point.value is None
                        else self._unit_registry.convert(
                            point.value,
                            source_unit,
                            target_unit,
                        )
                    ),
                )
                for point in series.points
            )

            normalized_series.append(
                TimeSeries(
                    series_id=series.series_id,
                    variable=target_variable,
                    location=replace(series.location),
                    temporal_resolution=series.temporal_resolution,
                    points=normalized_points,
                )
            )

            conversion_transformations.append(
                f"Converted series '{series.series_id}' from '{source_unit}' to '{target_unit}'."
            )

        transformations = (
            *dataset.provenance.transformations,
            *conversion_transformations,
            "Converted timestamps to UTC.",
            "Preserved missing observations as null values.",
            "Preserved spatial coordinates without changing geographic meaning.",
        )

        parent_dataset_ids = tuple(
            dict.fromkeys(
                (
                    *dataset.provenance.parent_dataset_ids,
                    dataset.dataset_id,
                )
            )
        )

        normalized_provenance = DataProvenance(
            source=dataset.provenance.source,
            retrieved_at=dataset.provenance.retrieved_at,
            source_record_id=dataset.provenance.source_record_id,
            transformations=transformations,
            parent_dataset_ids=parent_dataset_ids,
        )

        normalized_dataset = Dataset(
            dataset_id=f"{dataset.dataset_id}_normalized",
            request=replace(
                dataset.request,
                variable=target_variable,
            ),
            metadata=replace(
                dataset.metadata,
                title=f"{dataset.metadata.title} (Normalized)",
            ),
            provenance=normalized_provenance,
        )

        return NormalizationResult(
            dataset=normalized_dataset,
            time_series=tuple(normalized_series),
            transformations=transformations,
        )
