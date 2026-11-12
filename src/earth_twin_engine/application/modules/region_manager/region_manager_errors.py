"""Errors raised by the region management system."""


class RegionManagerError(Exception):
    """Base exception for region management errors."""


class DuplicateRegionError(RegionManagerError):
    """Raised when a region ID is already registered."""


class RegionNotFoundError(RegionManagerError):
    """Raised when a requested region does not exist."""
