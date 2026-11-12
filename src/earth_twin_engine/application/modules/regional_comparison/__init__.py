"""Regional comparison application module."""

from .commands import CompareRegionsCommand
from .errors import (
    InvalidRegionalComparisonError,
    RegionalComparisonDataError,
    RegionalComparisonError,
    RegionNotFoundForComparisonError,
)
from .events import (
    RegionalComparisonCompletedEvent,
    RegionalComparisonFailedEvent,
)
from .regional_comparison_handler import RegionalComparisonHandler
from .regional_comparison_module import RegionalComparisonModule
from .regional_comparison_result import (
    RegionalComparisonResult,
    RegionalTrendResult,
)
from .regional_comparison_service import RegionalComparisonService

__all__ = [
    "CompareRegionsCommand",
    "InvalidRegionalComparisonError",
    "RegionalComparisonCompletedEvent",
    "RegionalComparisonDataError",
    "RegionalComparisonError",
    "RegionalComparisonFailedEvent",
    "RegionalComparisonHandler",
    "RegionalComparisonModule",
    "RegionalComparisonResult",
    "RegionalComparisonService",
    "RegionalTrendResult",
    "RegionNotFoundForComparisonError",
]
