"""Tests for the regional comparison command handler."""

from uuid import uuid4

import pytest

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.regional_comparison import (
    CompareRegionsCommand,
    RegionalComparisonHandler,
    RegionalComparisonService,
)
from earth_twin_engine.application.modules.regional_comparison.events import (
    RegionalComparisonCompletedEvent,
    RegionalComparisonFailedEvent,
)
from earth_twin_engine.application.modules.trend_analysis import TrendAnalyzer


@pytest.fixture
def handler(
    region_manager,
    populated_time_series_manager,
) -> RegionalComparisonHandler:
    service = RegionalComparisonService(
        region_manager,
        populated_time_series_manager,
        TrendAnalyzer(),
    )

    return RegionalComparisonHandler(service, EventDispatcher())


def test_handler_publishes_completed_event(handler) -> None:
    events = []
    handler._event_dispatcher.subscribe(
        RegionalComparisonCompletedEvent,
        events.append,
    )
    command = CompareRegionsCommand(
        region_ids=("region_north", "region_south"),
        variable_id="surface_temperature",
    )

    result = handler.handle(command)

    assert len(events) == 1
    assert isinstance(events[0], RegionalComparisonCompletedEvent)
    assert events[0].result is result
    assert events[0].command_id == command.command_id
    assert events[0].correlation_id == command.correlation_id


def test_handler_publishes_failed_event_and_reraises_error(
    region_manager,
    time_series_manager,
) -> None:
    dispatcher = EventDispatcher()
    events = []
    dispatcher.subscribe(RegionalComparisonFailedEvent, events.append)

    service = RegionalComparisonService(
        region_manager,
        time_series_manager,
        TrendAnalyzer(),
    )
    handler = RegionalComparisonHandler(service, dispatcher)

    command = CompareRegionsCommand(
        region_ids=("region_north", "region_south"),
        variable_id="surface_temperature",
    )

    with pytest.raises(Exception, match="No time series"):
        handler.handle(command)

    assert len(events) == 1
    assert isinstance(events[0], RegionalComparisonFailedEvent)
    assert events[0].command_id == command.command_id
    assert events[0].variable_id == command.variable_id
    assert events[0].region_ids == command.region_ids
    assert events[0].error_type == "RegionalComparisonDataError"


def test_handler_preserves_correlation_id(handler) -> None:
    events = []
    handler._event_dispatcher.subscribe(
        RegionalComparisonCompletedEvent,
        events.append,
    )
    correlation_id = uuid4()

    command = CompareRegionsCommand(
        region_ids=("region_north", "region_south"),
        variable_id="surface_temperature",
        correlation_id=correlation_id,
    )

    handler.handle(command)

    assert events[0].correlation_id == correlation_id


def test_handler_rejects_invalid_command(handler) -> None:
    with pytest.raises(TypeError, match="CompareRegionsCommand"):
        handler.handle("invalid")  # type: ignore[arg-type]


def test_handler_rejects_invalid_dependencies() -> None:
    with pytest.raises(TypeError, match="RegionalComparisonService"):
        RegionalComparisonHandler(
            "invalid",
            EventDispatcher(),
        )
