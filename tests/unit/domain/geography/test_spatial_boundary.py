"""Tests for geographic boundaries."""

import pytest

from earth_twin_engine.domain.geography import (
    SpatialBoundary,
    SpatialCoordinate,
)


def create_boundary(**overrides: object) -> SpatialBoundary:
    values: dict[str, object] = {
        "south_latitude": 6.0,
        "north_latitude": 37.0,
        "west_longitude": 68.0,
        "east_longitude": 98.0,
    }
    values.update(overrides)
    return SpatialBoundary(**values)  # type: ignore[arg-type]


def test_create_valid_boundary() -> None:
    boundary = create_boundary()

    assert boundary.latitude_span_degrees == 31.0
    assert boundary.longitude_span_degrees == 30.0
    assert not boundary.crosses_antimeridian


def test_reject_invalid_latitude_order() -> None:
    with pytest.raises(ValueError, match="south_latitude"):
        create_boundary(south_latitude=40.0, north_latitude=30.0)


def test_reject_equal_latitudes() -> None:
    with pytest.raises(ValueError, match="south_latitude"):
        create_boundary(south_latitude=10.0, north_latitude=10.0)


def test_reject_invalid_longitude() -> None:
    with pytest.raises(ValueError, match="west_longitude"):
        create_boundary(west_longitude=-181.0)


def test_reject_equal_longitudes() -> None:
    with pytest.raises(ValueError, match="non-zero"):
        create_boundary(west_longitude=70.0, east_longitude=70.0)


def test_reject_non_numeric_boundary_value() -> None:
    with pytest.raises(TypeError):
        create_boundary(north_latitude=True)


def test_reject_non_finite_boundary_value() -> None:
    with pytest.raises(ValueError):
        create_boundary(east_longitude=float("nan"))


def test_contains_coordinate_inside_boundary() -> None:
    boundary = create_boundary()

    assert boundary.contains(SpatialCoordinate(20, 78))


def test_contains_boundary_edges() -> None:
    boundary = create_boundary()

    assert boundary.contains(SpatialCoordinate(6, 68))
    assert boundary.contains(SpatialCoordinate(37, 98))


def test_excludes_coordinate_outside_boundary() -> None:
    boundary = create_boundary()

    assert not boundary.contains(SpatialCoordinate(40, 78))
    assert not boundary.contains(SpatialCoordinate(20, 100))


def test_reject_invalid_coordinate_argument() -> None:
    boundary = create_boundary()

    with pytest.raises(TypeError, match="SpatialCoordinate"):
        boundary.contains((20, 78))  # type: ignore[arg-type]


def test_detect_antimeridian_crossing() -> None:
    boundary = create_boundary(
        south_latitude=-20,
        north_latitude=20,
        west_longitude=170,
        east_longitude=-170,
    )

    assert boundary.crosses_antimeridian
    assert boundary.longitude_span_degrees == 20.0


def test_contains_coordinates_across_antimeridian() -> None:
    boundary = create_boundary(
        south_latitude=-20,
        north_latitude=20,
        west_longitude=170,
        east_longitude=-170,
    )

    assert boundary.contains(SpatialCoordinate(0, 175))
    assert boundary.contains(SpatialCoordinate(0, -175))
    assert not boundary.contains(SpatialCoordinate(0, 0))


def test_boundary_is_immutable() -> None:
    boundary = create_boundary()

    with pytest.raises(AttributeError):
        boundary.north_latitude = 40  # type: ignore[misc]
