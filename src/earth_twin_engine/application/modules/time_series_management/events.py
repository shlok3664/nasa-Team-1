"""Events emitted by time-series management operations."""

from dataclasses import dataclass
from uuid import UUID

from earth_twin_engine.application.events.application_event import ApplicationEvent
from earth_twin_engine.domain.time_series import TimeSeries


@dataclass(frozen=True, slots=True, kw_only=True)
class TimeSeriesRegisteredEvent(ApplicationEvent):
    """Published after a time series is registered."""

    command_id: UUID
    correlation_id: UUID | None
    series_id: str

    def __post_init__(self) -> None:
        ApplicationEvent.__post_init__(self)

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None")

        if not isinstance(self.series_id, str) or not self.series_id.strip():
            raise ValueError("series_id must be a non-empty string")


@dataclass(frozen=True, slots=True, kw_only=True)
class TimeSeriesRemovedEvent(ApplicationEvent):
    """Published after a time series is removed."""

    command_id: UUID
    correlation_id: UUID | None
    series_id: str

    def __post_init__(self) -> None:
        ApplicationEvent.__post_init__(self)

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None")

        if not isinstance(self.series_id, str) or not self.series_id.strip():
            raise ValueError("series_id must be a non-empty string")


@dataclass(frozen=True, slots=True, kw_only=True)
class TimeSeriesAggregatedEvent(ApplicationEvent):
    """Published after a temporal or spatial aggregation succeeds."""

    command_id: UUID
    correlation_id: UUID | None
    source_series_ids: tuple[str, ...]
    result: TimeSeries

    def __post_init__(self) -> None:
        ApplicationEvent.__post_init__(self)

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None")

        if not isinstance(self.source_series_ids, tuple) or not self.source_series_ids:
            raise ValueError("source_series_ids must be a non-empty tuple")

        if not all(isinstance(item, str) and item.strip() for item in self.source_series_ids):
            raise ValueError("source_series_ids must contain non-empty strings")

        if not isinstance(self.result, TimeSeries):
            raise TypeError("result must be a TimeSeries")


@dataclass(frozen=True, slots=True, kw_only=True)
class TimeSeriesOperationFailedEvent(ApplicationEvent):
    """Published when a time-series command fails."""

    command_id: UUID
    correlation_id: UUID | None
    operation: str
    reason: str

    def __post_init__(self) -> None:
        ApplicationEvent.__post_init__(self)

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None")

        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string")

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
