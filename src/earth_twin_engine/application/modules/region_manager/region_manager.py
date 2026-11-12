"""Thread-safe geographic region registry and discovery manager."""

from threading import RLock

from earth_twin_engine.domain.geography import (
    GeographicRegion,
    SpatialCoordinate,
)

from .region_manager_errors import (
    DuplicateRegionError,
    RegionNotFoundError,
)


class RegionManager:
    """Registers, retrieves, and discovers geographic regions."""

    def __init__(self) -> None:
        self._regions: dict[str, GeographicRegion] = {}
        self._lock = RLock()

    @property
    def region_count(self) -> int:
        """Return the number of registered regions."""

        with self._lock:
            return len(self._regions)

    def register(self, region: GeographicRegion) -> None:
        """Register a geographic region."""

        if not isinstance(region, GeographicRegion):
            raise TypeError("region must be a GeographicRegion")

        with self._lock:
            if region.region_id in self._regions:
                raise DuplicateRegionError(f"Region '{region.region_id}' is already registered")

            self._regions[region.region_id] = region

    def unregister(self, region_id: str) -> bool:
        """Unregister a region, returning whether it existed."""

        self._validate_region_id(region_id)

        with self._lock:
            return self._regions.pop(region_id, None) is not None

    def get_region(self, region_id: str) -> GeographicRegion:
        """Retrieve a registered region by ID."""

        self._validate_region_id(region_id)

        with self._lock:
            region = self._regions.get(region_id)

            if region is None:
                raise RegionNotFoundError(f"Region '{region_id}' is not registered")

            return region

    def all_regions(self) -> tuple[GeographicRegion, ...]:
        """Return all registered regions sorted by region ID."""

        with self._lock:
            return tuple(self._regions[region_id] for region_id in sorted(self._regions))

    def find_containing(
        self,
        coordinate: SpatialCoordinate,
    ) -> tuple[GeographicRegion, ...]:
        """Find every registered region containing a coordinate."""

        if not isinstance(coordinate, SpatialCoordinate):
            raise TypeError("coordinate must be a SpatialCoordinate")

        with self._lock:
            return tuple(
                self._regions[region_id]
                for region_id in sorted(self._regions)
                if self._regions[region_id].boundary.contains(coordinate)
            )

    @staticmethod
    def _validate_region_id(region_id: str) -> None:
        """Validate a region identifier."""

        if not isinstance(region_id, str):
            raise TypeError("region_id must be a string")

        if not region_id.strip():
            raise ValueError("region_id must not be empty")
