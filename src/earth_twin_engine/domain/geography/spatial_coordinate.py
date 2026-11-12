"""Geographic coordinate value object."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class SpatialCoordinate:
    """Represents a WGS84 geographic coordinate.

    Latitude and longitude are expressed in decimal degrees.
    Elevation, when supplied, is expressed in meters above sea level.
    """

    latitude: float
    longitude: float
    elevation_meters: float | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("latitude", self.latitude),
            ("longitude", self.longitude),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a numeric value")

            if not isfinite(value):
                raise ValueError(f"{name} must be finite")

        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90 degrees")

        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180 degrees")

        if self.elevation_meters is not None:
            elevation = self.elevation_meters

            if isinstance(elevation, bool) or not isinstance(elevation, (int, float)):
                raise TypeError("elevation_meters must be numeric")

            if not isfinite(elevation):
                raise ValueError("elevation_meters must be finite")
