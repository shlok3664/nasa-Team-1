"""Regular geographic grid domain object."""

from dataclasses import dataclass

from earth_twin_engine.domain.geography.spatial_boundary import (
    SpatialBoundary,
)
from earth_twin_engine.domain.geography.spatial_coordinate import (
    SpatialCoordinate,
)


@dataclass(frozen=True, slots=True)
class SpatialGrid:
    """Represents a regular grid over a geographic boundary."""

    boundary: SpatialBoundary
    rows: int
    columns: int

    def __post_init__(self) -> None:
        if not isinstance(self.boundary, SpatialBoundary):
            raise TypeError("boundary must be a SpatialBoundary")

        for name, value in (
            ("rows", self.rows),
            ("columns", self.columns),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")

            if value <= 0:
                raise ValueError(f"{name} must be positive")

    @property
    def cell_count(self) -> int:
        """Return the total number of grid cells."""

        return self.rows * self.columns

    @property
    def latitude_resolution_degrees(self) -> float:
        """Return the latitude span of one cell."""

        return self.boundary.latitude_span_degrees / self.rows

    @property
    def longitude_resolution_degrees(self) -> float:
        """Return the longitude span of one cell."""

        return self.boundary.longitude_span_degrees / self.columns

    def cell_center(self, row: int, column: int) -> SpatialCoordinate:
        """Return the geographic center of a grid cell.

        Row zero is the southernmost row. Column zero starts
        at the western boundary.
        """

        if isinstance(row, bool) or not isinstance(row, int):
            raise TypeError("row must be an integer")

        if isinstance(column, bool) or not isinstance(column, int):
            raise TypeError("column must be an integer")

        if not 0 <= row < self.rows:
            raise IndexError("row is outside the grid")

        if not 0 <= column < self.columns:
            raise IndexError("column is outside the grid")

        latitude = self.boundary.south_latitude + (row + 0.5) * self.latitude_resolution_degrees

        longitude_offset = (column + 0.5) * self.longitude_resolution_degrees

        longitude = self.boundary.west_longitude + longitude_offset

        if longitude > 180:
            longitude -= 360

        return SpatialCoordinate(
            latitude=latitude,
            longitude=longitude,
        )
