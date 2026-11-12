"""Geographic region management application module."""

from .queries import (
    FindRegionsContainingQuery,
    GetGeographicRegionQuery,
    ListGeographicRegionsQuery,
)
from .query_handlers import (
    FindRegionsContainingHandler,
    GetGeographicRegionHandler,
    ListGeographicRegionsHandler,
)
from .region_manager import RegionManager
from .region_manager_errors import (
    DuplicateRegionError,
    RegionManagerError,
    RegionNotFoundError,
)
from .region_manager_module import RegionManagerModule

__all__ = [
    "DuplicateRegionError",
    "FindRegionsContainingHandler",
    "FindRegionsContainingQuery",
    "GetGeographicRegionHandler",
    "GetGeographicRegionQuery",
    "ListGeographicRegionsHandler",
    "ListGeographicRegionsQuery",
    "RegionManager",
    "RegionManagerError",
    "RegionManagerModule",
    "RegionNotFoundError",
]
