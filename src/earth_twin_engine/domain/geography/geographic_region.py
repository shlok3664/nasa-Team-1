"""Geographic region domain entity."""

import re
from dataclasses import dataclass

from earth_twin_engine.domain.geography.spatial_boundary import (
    SpatialBoundary,
)

_REGION_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class GeographicRegion:
    """Represents a named geographic area."""

    region_id: str
    name: str
    boundary: SpatialBoundary
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.region_id, str):
            raise TypeError("region_id must be a string")

        if not _REGION_ID_PATTERN.fullmatch(self.region_id):
            raise ValueError(
                "region_id must use lowercase letters, numbers, "
                "and underscores, starting with a letter"
            )

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")

        if not isinstance(self.boundary, SpatialBoundary):
            raise TypeError("boundary must be a SpatialBoundary")

        if not isinstance(self.description, str):
            raise TypeError("description must be a string")
