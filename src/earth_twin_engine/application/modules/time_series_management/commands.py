"""Commands for time-series management."""

from dataclasses import dataclass

from earth_twin_engine.application.commands.application_command import (
    ApplicationCommand,
)
from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import TimeSeries

from .aggregation.aggregation_method import AggregationMethod


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterTimeSeriesCommand(ApplicationCommand):
    """Register a time series with the manager."""

    series: TimeSeries

    def __post_init__(self) -> None:
        ApplicationCommand.__post_init__(self)

        if not isinstance(self.series, TimeSeries):
            raise TypeError("series must be a TimeSeries")


@dataclass(frozen=True, slots=True, kw_only=True)
class RemoveTimeSeriesCommand(ApplicationCommand):
    """Remove a registered time series."""

    series_id: str

    def __post_init__(self) -> None:
        ApplicationCommand.__post_init__(self)

        if not isinstance(self.series_id, str) or not self.series_id.strip():
            raise ValueError("series_id must be a non-empty string")


@dataclass(frozen=True, slots=True, kw_only=True)
class AggregateTimeSeriesCommand(ApplicationCommand):
    """Aggregate a registered series into a coarser temporal resolution."""

    series_id: str
    target_resolution: TemporalResolution
    method: AggregationMethod = AggregationMethod.MEAN

    def __post_init__(self) -> None:
        ApplicationCommand.__post_init__(self)

        if not isinstance(self.series_id, str) or not self.series_id.strip():
            raise ValueError("series_id must be a non-empty string")

        if not isinstance(self.target_resolution, TemporalResolution):
            raise TypeError("target_resolution must be a TemporalResolution")

        if not isinstance(self.method, AggregationMethod):
            raise TypeError("method must be an AggregationMethod")


@dataclass(frozen=True, slots=True, kw_only=True)
class AggregateSpatialTimeSeriesCommand(ApplicationCommand):
    """Aggregate multiple registered series across their locations."""

    series_ids: tuple[str, ...]
    result_series_id: str
    method: AggregationMethod = AggregationMethod.MEAN

    def __post_init__(self) -> None:
        ApplicationCommand.__post_init__(self)

        if not isinstance(self.series_ids, tuple):
            raise TypeError("series_ids must be a tuple")

        if len(self.series_ids) < 2:
            raise ValueError("at least two series identifiers are required")

        if any(not isinstance(item, str) or not item.strip() for item in self.series_ids):
            raise ValueError("series_ids must contain non-empty strings")

        if len(set(self.series_ids)) != len(self.series_ids):
            raise ValueError("series_ids cannot contain duplicates")

        if not isinstance(self.result_series_id, str) or not self.result_series_id.strip():
            raise ValueError("result_series_id must be a non-empty string")

        if not isinstance(self.method, AggregationMethod):
            raise TypeError("method must be an AggregationMethod")
