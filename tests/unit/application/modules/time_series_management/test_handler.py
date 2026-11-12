"""Tests for time-series management command handling."""

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.time_series_management import (
    AggregateTimeSeriesCommand,
    RegisterTimeSeriesCommand,
    TimeSeriesAggregatedEvent,
    TimeSeriesManagementHandler,
    TimeSeriesManager,
    TimeSeriesRegisteredEvent,
)
from earth_twin_engine.application.modules.time_series_management.aggregation import (
    SpatialAggregator,
    TemporalAggregator,
)
from earth_twin_engine.domain.temporal import TemporalResolution


def create_handler():
    dispatcher = EventDispatcher()
    manager = TimeSeriesManager()

    handler = TimeSeriesManagementHandler(
        manager=manager,
        temporal_aggregator=TemporalAggregator(),
        spatial_aggregator=SpatialAggregator(),
        event_dispatcher=dispatcher,
    )

    return handler, manager, dispatcher


def test_register_command_publishes_event(hourly_series) -> None:
    handler, manager, dispatcher = create_handler()
    received = []
    dispatcher.subscribe(TimeSeriesRegisteredEvent, received.append)

    handler.handle(RegisterTimeSeriesCommand(series=hourly_series))

    assert manager.get(hourly_series.series_id) is hourly_series
    assert len(received) == 1
    assert received[0].series_id == hourly_series.series_id


def test_temporal_aggregation_command_registers_result(hourly_series) -> None:
    handler, manager, dispatcher = create_handler()
    received = []
    dispatcher.subscribe(TimeSeriesAggregatedEvent, received.append)

    manager.register(hourly_series)

    result = handler.handle(
        AggregateTimeSeriesCommand(
            series_id=hourly_series.series_id,
            target_resolution=TemporalResolution.DAILY,
        )
    )

    assert manager.get(result.series_id) is result
    assert len(received) == 1
    assert received[0].result is result
    assert received[0].source_series_ids == (hourly_series.series_id,)
