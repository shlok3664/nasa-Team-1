"""Tests for geographic coordinates."""

import pytest

from earth_twin_engine.domain.geography import SpatialCoordinate


def test_create_valid_coordinate() -> None:
    coordinate = SpatialCoordinate(
        latitude=20.5937,
        longitude=78.9629,
        elevation_meters=500.0,
    )

    assert coordinate.latitude == 20.5937
    assert coordinate.longitude == 78.9629
    assert coordinate.elevation_meters == 500.0


def test_allow_missing_elevation() -> None:
    coordinate = SpatialCoordinate(latitude=0, longitude=0)

    assert coordinate.elevation_meters is None


@pytest.mark.parametrize("latitude", [-90, 90, 0])
def test_accept_valid_latitudes(latitude: float) -> None:
    assert SpatialCoordinate(latitude, 0).latitude == latitude


@pytest.mark.parametrize("latitude", [-90.1, 90.1])
def test_reject_out_of_range_latitude(latitude: float) -> None:
    with pytest.raises(ValueError, match="latitude"):
        SpatialCoordinate(latitude, 0)


@pytest.mark.parametrize("longitude", [-180, 180, 0])
def test_accept_valid_longitudes(longitude: float) -> None:
    assert SpatialCoordinate(0, longitude).longitude == longitude


@pytest.mark.parametrize("longitude", [-180.1, 180.1])
def test_reject_out_of_range_longitude(longitude: float) -> None:
    with pytest.raises(ValueError, match="longitude"):
        SpatialCoordinate(0, longitude)


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_reject_non_finite_coordinates(value: float) -> None:
    with pytest.raises(ValueError):
        SpatialCoordinate(value, 0)


def test_reject_boolean_coordinates() -> None:
    with pytest.raises(TypeError, match="latitude"):
        SpatialCoordinate(True, 0)


def test_reject_invalid_elevation_type() -> None:
    with pytest.raises(TypeError, match="elevation"):
        SpatialCoordinate(0, 0, True)


def test_reject_non_finite_elevation() -> None:
    with pytest.raises(ValueError, match="elevation"):
        SpatialCoordinate(0, 0, float("inf"))


def test_coordinate_is_immutable() -> None:
    coordinate = SpatialCoordinate(10, 20)

    with pytest.raises(AttributeError):
        coordinate.latitude = 30  # type: ignore[misc]
