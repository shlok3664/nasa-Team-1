"""Tests for scientific data requests."""

from datetime import UTC, datetime

import pytest

from earth_twin_engine.domain.datasets import DataRequest
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


def create_request(**overrides: object) -> DataRequest:
    variable = EarthVariable(
        variable_id="air_temperature",
        name="Air Temperature",
        description="Near-surface atmospheric air temperature.",
        category=VariableCategory.ATMOSPHERE,
        metadata=VariableMetadata(
            unit="K",
            temporal_resolutions=(
                TemporalResolution.HOURLY,
                TemporalResolution.DAILY,
            ),
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

    temporal_range = TemporalRange(
        start=datetime(2020, 1, 1, tzinfo=UTC),
        end=datetime(2021, 1, 1, tzinfo=UTC),
    )

    values: dict[str, object] = {
        "variable": variable,
        "region": region,
        "temporal_range": temporal_range,
        "temporal_resolution": TemporalResolution.DAILY,
        "source_id": "nasa_merra2",
    }
    values.update(overrides)

    return DataRequest(**values)  # type: ignore[arg-type]


def test_create_valid_data_request() -> None:
    request = create_request()

    assert request.variable.variable_id == "air_temperature"
    assert request.region.region_id == "india"
    assert request.temporal_resolution is TemporalResolution.DAILY
    assert request.source_id == "nasa_merra2"


def test_allow_unspecified_source() -> None:
    request = create_request(source_id=None)

    assert request.source_id is None


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("variable", None, "EarthVariable"),
        ("region", None, "GeographicRegion"),
        ("temporal_range", None, "TemporalRange"),
        ("temporal_resolution", "daily", "TemporalResolution"),
    ],
)
def test_reject_invalid_contract_types(
    field: str,
    value: object,
    expected_error: str,
) -> None:
    with pytest.raises(TypeError, match=expected_error):
        create_request(**{field: value})


def test_reject_unsupported_temporal_resolution() -> None:
    with pytest.raises(ValueError, match="not supported"):
        create_request(temporal_resolution=TemporalResolution.MONTHLY)


def test_reject_empty_source_id() -> None:
    with pytest.raises(ValueError, match="source_id"):
        create_request(source_id=" ")


def test_reject_non_string_source_id() -> None:
    with pytest.raises(ValueError, match="source_id"):
        create_request(source_id=123)


def test_data_request_is_immutable() -> None:
    request = create_request()

    with pytest.raises(AttributeError):
        request.source_id = None  # type: ignore[misc]
