"""Geographic boundary value object."""

from dataclasses import dataclass
from math import isfinite

from earth_twin_engine.domain.geography.spatial_coordinate import (
    SpatialCoordinate,
)


@dataclass(frozen=True, slots=True)
class SpatialBoundary:
    """Represents a rectangular geographic boundary.

    Longitude may cross the antimeridian. For example, west=170
    and east=-170 represents a 20-degree-wide region.
    """

    south_latitude: float
    north_latitude: float
    west_longitude: float
    east_longitude: float

    def __post_init__(self) -> None:
        values = {
            "south_latitude": self.south_latitude,
            "north_latitude": self.north_latitude,
            "west_longitude": self.west_longitude,
            "east_longitude": self.east_longitude,
        }

        for name, value in values.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be numeric")

            if not isfinite(value):
                raise ValueError(f"{name} must be finite")

        if not -90 <= self.south_latitude <= 90:
            raise ValueError("south_latitude must be between -90 and 90")

        if not -90 <= self.north_latitude <= 90:
            raise ValueError("north_latitude must be between -90 and 90")

        if self.south_latitude >= self.north_latitude:
            raise ValueError("south_latitude must be less than north_latitude")

        if not -180 <= self.west_longitude <= 180:
            raise ValueError("west_longitude must be between -180 and 180")

        if not -180 <= self.east_longitude <= 180:
            raise ValueError("east_longitude must be between -180 and 180")

        if self.west_longitude == self.east_longitude:
            raise ValueError("boundary must have a non-zero longitude span")

    @property
    def crosses_antimeridian(self) -> bool:
        """Return whether the boundary crosses the antimeridian."""

        return self.west_longitude > self.east_longitude

    @property
    def longitude_span_degrees(self) -> float:
        """Return the longitudinal span in degrees."""

        if self.crosses_antimeridian:
            return 180 - self.west_longitude + self.east_longitude + 180

        return self.east_longitude - self.west_longitude

    @property
    def latitude_span_degrees(self) -> float:
        """Return the latitudinal span in degrees."""

        return self.north_latitude - self.south_latitude

    def contains(self, coordinate: SpatialCoordinate) -> bool:
        """Check whether a coordinate lies inside this boundary."""

        if not isinstance(coordinate, SpatialCoordinate):
            raise TypeError("coordinate must be a SpatialCoordinate")

        latitude_inside = self.south_latitude <= coordinate.latitude <= self.north_latitude

        if self.crosses_antimeridian:
            longitude_inside = (
                coordinate.longitude >= self.west_longitude
                or coordinate.longitude <= self.east_longitude
            )
        else:
            longitude_inside = self.west_longitude <= coordinate.longitude <= self.east_longitude

        return latitude_inside and longitude_inside
