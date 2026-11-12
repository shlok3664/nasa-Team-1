"""Command handling for time-series management."""

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.time_series_management.aggregation import (
    SpatialAggregator,
    TemporalAggregator,
)
from earth_twin_engine.application.modules.time_series_management.commands import (
    AggregateSpatialTimeSeriesCommand,
    AggregateTimeSeriesCommand,
    RegisterTimeSeriesCommand,
    RemoveTimeSeriesCommand,
)
from earth_twin_engine.application.modules.time_series_management.events import (
    TimeSeriesAggregatedEvent,
    TimeSeriesOperationFailedEvent,
    TimeSeriesRegisteredEvent,
    TimeSeriesRemovedEvent,
)
from earth_twin_engine.application.modules.time_series_management.time_series_manager import (
    TimeSeriesManager,
)


class TimeSeriesManagementHandler:
    """Executes time-series commands and publishes their outcomes."""

    def __init__(
        self,
        manager: TimeSeriesManager,
        temporal_aggregator: TemporalAggregator,
        spatial_aggregator: SpatialAggregator,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self._manager = manager
        self._temporal_aggregator = temporal_aggregator
        self._spatial_aggregator = spatial_aggregator
        self._event_dispatcher = event_dispatcher

    def handle(
        self,
        command: (
            RegisterTimeSeriesCommand
            | RemoveTimeSeriesCommand
            | AggregateTimeSeriesCommand
            | AggregateSpatialTimeSeriesCommand
        ),
    ):
        """Dispatch a supported command to its operation."""

        if isinstance(command, RegisterTimeSeriesCommand):
            return self._register(command)

        if isinstance(command, RemoveTimeSeriesCommand):
            return self._remove(command)

        if isinstance(command, AggregateTimeSeriesCommand):
            return self._aggregate_temporal(command)

        if isinstance(command, AggregateSpatialTimeSeriesCommand):
            return self._aggregate_spatial(command)

        raise TypeError(f"Unsupported command type: {type(command).__name__}")

    def _register(self, command: RegisterTimeSeriesCommand) -> None:
        try:
            self._manager.register(command.series)
            self._event_dispatcher.publish(
                TimeSeriesRegisteredEvent(
                    command_id=command.command_id,
                    correlation_id=command.correlation_id,
                    series_id=command.series.series_id,
                )
            )
        except Exception as exc:
            self._publish_failure(command, "register", exc)
            raise

    def _remove(self, command: RemoveTimeSeriesCommand) -> bool:
        try:
            removed = self._manager.unregister(command.series_id)

            if removed:
                self._event_dispatcher.publish(
                    TimeSeriesRemovedEvent(
                        command_id=command.command_id,
                        correlation_id=command.correlation_id,
                        series_id=command.series_id,
                    )
                )

            return removed
        except Exception as exc:
            self._publish_failure(command, "remove", exc)
            raise

    def _aggregate_temporal(self, command: AggregateTimeSeriesCommand):
        try:
            source = self._manager.get(command.series_id)
            result = self._temporal_aggregator.aggregate(
                series=source,
                target_resolution=command.target_resolution,
                method=command.method,
            )
            self._manager.register(result)
            self._publish_aggregation(command, (source.series_id,), result)
            return result
        except Exception as exc:
            self._publish_failure(command, "temporal_aggregation", exc)
            raise

    def _aggregate_spatial(self, command: AggregateSpatialTimeSeriesCommand):
        try:
            sources = tuple(self._manager.get(series_id) for series_id in command.series_ids)
            result = self._spatial_aggregator.aggregate(
                series=sources,
                series_id=command.result_series_id,
                method=command.method,
            )
            self._manager.register(result)
            self._publish_aggregation(command, command.series_ids, result)
            return result
        except Exception as exc:
            self._publish_failure(command, "spatial_aggregation", exc)
            raise

    def _publish_aggregation(self, command, source_ids, result) -> None:
        self._event_dispatcher.publish(
            TimeSeriesAggregatedEvent(
                command_id=command.command_id,
                correlation_id=command.correlation_id,
                source_series_ids=source_ids,
                result=result,
            )
        )

    def _publish_failure(self, command, operation: str, error: Exception) -> None:
        self._event_dispatcher.publish(
            TimeSeriesOperationFailedEvent(
                command_id=command.command_id,
                correlation_id=command.correlation_id,
                operation=operation,
                reason=str(error) or type(error).__name__,
            )
        )
