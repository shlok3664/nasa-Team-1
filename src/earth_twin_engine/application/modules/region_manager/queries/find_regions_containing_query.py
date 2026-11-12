"""Query for finding geographic regions containing a coordinate."""

from dataclasses import dataclass

from earth_twin_engine.application.queries import ApplicationQuery
from earth_twin_engine.domain.geography import SpatialCoordinate


@dataclass(frozen=True, slots=True, kw_only=True)
class FindRegionsContainingQuery(ApplicationQuery):
    """Requests regions containing a geographic coordinate."""

    coordinate: SpatialCoordinate

    def __post_init__(self) -> None:
        super(FindRegionsContainingQuery, self).__post_init__()

        if not isinstance(self.coordinate, SpatialCoordinate):
            raise TypeError("coordinate must be a SpatialCoordinate")
