"""Scientific time-series domain contracts."""

from earth_twin_engine.domain.time_series.aggregation_metadata import (
    AggregationMetadata,
)
from earth_twin_engine.domain.time_series.time_series import TimeSeries
from earth_twin_engine.domain.time_series.time_series_point import (
    TimeSeriesPoint,
)

__all__ = [
    "AggregationMetadata",
    "TimeSeries",
    "TimeSeriesPoint",
]
