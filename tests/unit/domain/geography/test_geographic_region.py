"""Tests for geographic regions."""

import pytest

from earth_twin_engine.domain.geography import (
    GeographicRegion,
    SpatialBoundary,
)


def create_region(**overrides: object) -> GeographicRegion:
    boundary = SpatialBoundary(
        south_latitude=6,
        north_latitude=37,
        west_longitude=68,
        east_longitude=98,
    )

    values: dict[str, object] = {
        "region_id": "india",
        "name": "India",
        "boundary": boundary,
        "description": "Geographic extent of India.",
    }
    values.update(overrides)

    return GeographicRegion(**values)  # type: ignore[arg-type]


def test_create_valid_geographic_region() -> None:
    region = create_region()

    assert region.region_id == "india"
    assert region.name == "India"
    assert region.boundary.south_latitude == 6


@pytest.mark.parametrize(
    "region_id",
    ["", "India", "india-region", "1india", "india region"],
)
def test_reject_invalid_region_id(region_id: str) -> None:
    with pytest.raises(ValueError, match="region_id"):
        create_region(region_id=region_id)


def test_reject_non_string_region_id() -> None:
    with pytest.raises(TypeError, match="region_id"):
        create_region(region_id=123)


def test_reject_empty_name() -> None:
    with pytest.raises(ValueError, match="name"):
        create_region(name=" ")


def test_reject_invalid_boundary() -> None:
    with pytest.raises(TypeError, match="SpatialBoundary"):
        create_region(boundary=None)


def test_reject_non_string_description() -> None:
    with pytest.raises(TypeError, match="description"):
        create_region(description=123)


def test_allow_empty_description() -> None:
    region = create_region(description="")

    assert region.description == ""


def test_region_is_immutable() -> None:
    region = create_region()

    with pytest.raises(AttributeError):
        region.name = "Changed"  # type: ignore[misc]
