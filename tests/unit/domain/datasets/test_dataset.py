"""Tests for scientific datasets."""

from datetime import UTC, datetime

import pytest

from earth_twin_engine.domain.datasets import (
    DataProvenance,
    DataRequest,
    Dataset,
    DatasetMetadata,
    DataSource,
)
from earth_twin_engine.domain.geography import (
    GeographicRegion,
    SpatialBoundary,
)
from earth_twin_engine.domain.temporal import (
    TemporalRange,
    TemporalResolution,
)
from earth_twin_engine.domain.variables import (
    EarthVariable,
    VariableCategory,
    VariableMetadata,
)


def create_dataset(**overrides: object) -> Dataset:
    variable = EarthVariable(
        variable_id="air_temperature",
        name="Air Temperature",
        description="Near-surface atmospheric air temperature.",
        category=VariableCategory.ATMOSPHERE,
        metadata=VariableMetadata(
            unit="K",
            temporal_resolutions=(TemporalResolution.DAILY,),
        ),
    )

    region = GeographicRegion(
        region_id="india",
        name="India",
        boundary=SpatialBoundary(
            south_latitude=6,
            north_latitude=37,
            west_longitude=68,
            east_longitude=98,
        ),
    )

    request = DataRequest(
        variable=variable,
        region=region,
        temporal_range=TemporalRange(
            start=datetime(2020, 1, 1, tzinfo=UTC),
            end=datetime(2021, 1, 1, tzinfo=UTC),
        ),
        temporal_resolution=TemporalResolution.DAILY,
        source_id="nasa_merra2",
    )

    source = DataSource(
        source_id="nasa_merra2",
        name="MERRA-2",
        provider="NASA",
    )

    metadata = DatasetMetadata(
        title="India Daily Temperature",
        data_format="NetCDF",
    )

    provenance = DataProvenance(
        source=source,
        retrieved_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    values: dict[str, object] = {
        "dataset_id": "india_daily_temperature",
        "request": request,
        "metadata": metadata,
        "provenance": provenance,
    }
    values.update(overrides)

    return Dataset(**values)  # type: ignore[arg-type]


def test_create_valid_dataset() -> None:
    dataset = create_dataset()

    assert dataset.dataset_id == "india_daily_temperature"
    assert dataset.request.variable.variable_id == "air_temperature"
    assert dataset.request.region.region_id == "india"
    assert dataset.provenance.source.source_id == "nasa_merra2"


@pytest.mark.parametrize(
    "dataset_id",
    ["", "India", "india-temperature", "1dataset", "india dataset"],
)
def test_reject_invalid_dataset_id(dataset_id: str) -> None:
    with pytest.raises(ValueError, match="dataset_id"):
        create_dataset(dataset_id=dataset_id)


def test_reject_non_string_dataset_id() -> None:
    with pytest.raises(TypeError, match="dataset_id"):
        create_dataset(dataset_id=123)


@pytest.mark.parametrize(
    ("field", "expected_error"),
    [
        ("request", "DataRequest"),
        ("metadata", "DatasetMetadata"),
        ("provenance", "DataProvenance"),
    ],
)
def test_reject_invalid_contracts(
    field: str,
    expected_error: str,
) -> None:
    with pytest.raises(TypeError, match=expected_error):
        create_dataset(**{field: None})


def test_reject_mismatched_requested_and_actual_source() -> None:
    source = DataSource(
        source_id="nasa_airs",
        name="AIRS",
        provider="NASA",
    )

    provenance = DataProvenance(
        source=source,
        retrieved_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    with pytest.raises(ValueError, match="does not match"):
        create_dataset(provenance=provenance)


def test_allow_unspecified_request_source() -> None:
    dataset = create_dataset()

    request = DataRequest(
        variable=dataset.request.variable,
        region=dataset.request.region,
        temporal_range=dataset.request.temporal_range,
        temporal_resolution=TemporalResolution.DAILY,
    )

    dataset = create_dataset(request=request)

    assert dataset.request.source_id is None


def test_reject_dataset_as_its_own_parent() -> None:
    dataset = create_dataset()
    provenance = DataProvenance(
        source=dataset.provenance.source,
        retrieved_at=datetime(2026, 1, 1, tzinfo=UTC),
        parent_dataset_ids=(dataset.dataset_id,),
    )

    with pytest.raises(ValueError, match="own parent"):
        create_dataset(provenance=provenance)


def test_dataset_is_immutable() -> None:
    dataset = create_dataset()

    with pytest.raises(AttributeError):
        dataset.dataset_id = "changed"  # type: ignore[misc]
