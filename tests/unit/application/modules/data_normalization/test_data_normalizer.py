"""Tests for scientific data normalization."""

from dataclasses import replace
from datetime import UTC

import pytest

from earth_twin_engine.application.modules.data_normalization import (
    DataNormalizer,
    UnitConversionRegistry,
    VariableMismatchError,
)
from earth_twin_engine.application.modules.data_normalization.normalization_error import (
    UnsupportedUnitConversionError,
)
from earth_twin_engine.domain.temporal import TemporalResolution


def test_normalizer_converts_units_and_preserves_missing_values(
    dataset,
    celsius_series_collection,
) -> None:
    result = DataNormalizer().normalize(dataset, celsius_series_collection)

    normalized_series = result.time_series[0]

    assert normalized_series.points[0].value == pytest.approx(285.4)
    assert normalized_series.points[1].value == pytest.approx(286.15)
    assert normalized_series.points[2].value is None


def test_normalizer_standardizes_timestamps_to_utc(
    dataset,
    celsius_series_collection,
) -> None:
    result = DataNormalizer().normalize(dataset, celsius_series_collection)

    for point in result.time_series[0].points:
        assert point.timestamp.utcoffset().total_seconds() == 0
        assert point.timestamp.tzinfo is UTC


def test_normalizer_preserves_spatial_coordinates(
    dataset,
    celsius_series_collection,
) -> None:
    original_location = celsius_series_collection[0].location

    result = DataNormalizer().normalize(dataset, celsius_series_collection)

    normalized_location = result.time_series[0].location

    assert normalized_location == original_location
    assert normalized_location is not original_location


def test_normalizer_uses_canonical_variable(
    dataset,
    celsius_series_collection,
) -> None:
    result = DataNormalizer().normalize(dataset, celsius_series_collection)

    assert result.time_series[0].variable is dataset.request.variable
    assert result.dataset.request.variable is dataset.request.variable


def test_normalizer_creates_derived_dataset(
    dataset,
    celsius_series_collection,
) -> None:
    result = DataNormalizer().normalize(dataset, celsius_series_collection)

    assert result.dataset.dataset_id == f"{dataset.dataset_id}_normalized"
    assert result.dataset.metadata.title.endswith("(Normalized)")
    assert result.dataset.dataset_id != dataset.dataset_id


def test_normalizer_preserves_original_dataset(
    dataset,
    celsius_series_collection,
) -> None:
    original_title = dataset.metadata.title
    original_series = celsius_series_collection[0]

    DataNormalizer().normalize(dataset, celsius_series_collection)

    assert dataset.metadata.title == original_title
    assert original_series.points[0].value == 12.25
    assert original_series.variable.metadata.unit == "C"


def test_normalizer_preserves_provenance_and_records_lineage(
    dataset,
    celsius_series_collection,
) -> None:
    result = DataNormalizer().normalize(dataset, celsius_series_collection)

    provenance = result.dataset.provenance

    assert provenance.source is dataset.provenance.source
    assert provenance.retrieved_at == dataset.provenance.retrieved_at
    assert dataset.dataset_id in provenance.parent_dataset_ids
    assert "Retrieved from NASA MERRA-2." in provenance.transformations
    assert any("Converted series" in item for item in provenance.transformations)


def test_normalizer_returns_transformation_descriptions(
    dataset,
    celsius_series_collection,
) -> None:
    result = DataNormalizer().normalize(dataset, celsius_series_collection)

    assert result.transformations
    assert any("UTC" in item for item in result.transformations)
    assert any("C" in item and "K" in item for item in result.transformations)


def test_normalizer_accepts_empty_series_collection(dataset) -> None:
    result = DataNormalizer().normalize(dataset, ())

    assert result.time_series == ()
    assert result.dataset.dataset_id.endswith("_normalized")


def test_normalizer_rejects_variable_mismatch(
    dataset,
    celsius_variable,
    celsius_series_collection,
) -> None:
    wrong_variable = replace(
        celsius_variable,
        variable_id="precipitation",
    )

    wrong_series = replace(
        celsius_series_collection[0],
        variable=wrong_variable,
    )

    with pytest.raises(VariableMismatchError):
        DataNormalizer().normalize(dataset, (wrong_series,))


def test_normalizer_rejects_unsupported_unit_conversion(
    dataset,
    celsius_series_collection,
) -> None:
    registry = UnitConversionRegistry(include_defaults=False)

    with pytest.raises(UnsupportedUnitConversionError, match="No conversion"):
        DataNormalizer(registry).normalize(dataset, celsius_series_collection)


def test_normalizer_accepts_custom_unit_conversion(
    dataset,
    celsius_series_collection,
) -> None:
    registry = UnitConversionRegistry(include_defaults=False)
    registry.register("c", "k", 1, 273.15)

    result = DataNormalizer(registry).normalize(
        dataset,
        celsius_series_collection,
    )

    assert result.time_series[0].points[0].value == pytest.approx(285.4)


def test_normalizer_rejects_invalid_dataset(celsius_series_collection) -> None:
    with pytest.raises(TypeError, match="Dataset"):
        DataNormalizer().normalize(None, celsius_series_collection)


def test_normalizer_rejects_non_tuple_series(dataset) -> None:
    with pytest.raises(TypeError, match="tuple"):
        DataNormalizer().normalize(dataset, [])


def test_normalizer_rejects_invalid_series_member(dataset) -> None:
    with pytest.raises(TypeError, match="TimeSeries"):
        DataNormalizer().normalize(dataset, ("invalid",))


def test_normalizer_rejects_invalid_registry() -> None:
    with pytest.raises(TypeError, match="UnitConversionRegistry"):
        DataNormalizer("invalid")


def test_normalizer_preserves_series_resolution(
    dataset,
    celsius_series_collection,
) -> None:
    result = DataNormalizer().normalize(dataset, celsius_series_collection)

    assert result.time_series[0].temporal_resolution is TemporalResolution.DAILY
