"""Time-series management application module."""

from .aggregation import (
    AggregationMethod,
    MissingPeriodDetector,
    SpatialAggregator,
    TemporalAggregator,
)
from .commands import (
    AggregateSpatialTimeSeriesCommand,
    AggregateTimeSeriesCommand,
    RegisterTimeSeriesCommand,
    RemoveTimeSeriesCommand,
)
from .errors import (
    DuplicateTimeSeriesError,
    IncompatibleTimeSeriesError,
    TimeSeriesAggregationError,
    TimeSeriesManagementError,
    TimeSeriesNotFoundError,
)
from .events import (
    TimeSeriesAggregatedEvent,
    TimeSeriesOperationFailedEvent,
    TimeSeriesRegisteredEvent,
    TimeSeriesRemovedEvent,
)
from .time_series_management_handler import TimeSeriesManagementHandler
from .time_series_management_module import TimeSeriesManagementModule
from .time_series_manager import TimeSeriesManager

__all__ = [
    "AggregateSpatialTimeSeriesCommand",
    "AggregateTimeSeriesCommand",
    "AggregationMethod",
    "DuplicateTimeSeriesError",
    "IncompatibleTimeSeriesError",
    "MissingPeriodDetector",
    "RegisterTimeSeriesCommand",
    "RemoveTimeSeriesCommand",
    "SpatialAggregator",
    "TemporalAggregator",
    "TimeSeriesAggregatedEvent",
    "TimeSeriesAggregationError",
    "TimeSeriesManagementError",
    "TimeSeriesManagementHandler",
    "TimeSeriesManagementModule",
    "TimeSeriesManager",
    "TimeSeriesNotFoundError",
    "TimeSeriesOperationFailedEvent",
    "TimeSeriesRegisteredEvent",
    "TimeSeriesRemovedEvent",
]
