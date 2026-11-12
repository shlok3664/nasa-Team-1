"""Tests for the statistical testing command handler."""

import pytest

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.statistical_testing import (
    MannKendallTest,
    RunStatisticalTestCommand,
    StatisticalTestCompletedEvent,
    StatisticalTestFailedEvent,
    StatisticalTestingError,
    StatisticalTestingHandler,
    StatisticalTestingService,
    StatisticalTestMethod,
    StatisticalTestRegistry,
)
from earth_twin_engine.application.modules.time_series_management import (
    TimeSeriesManager,
)


@pytest.fixture
def handler_setup(make_series):
    manager = TimeSeriesManager()
    manager.register(
        make_series(
            "handler_temperature",
            [10.0, 12.0, 14.0, 16.0, 18.0, 20.0],
        )
    )

    registry = StatisticalTestRegistry()
    registry.register(MannKendallTest())

    dispatcher = EventDispatcher()
    handler = StatisticalTestingHandler(
        manager=manager,
        service=StatisticalTestingService(registry),
        event_dispatcher=dispatcher,
    )

    return manager, dispatcher, handler


def test_handler_publishes_completed_event(handler_setup) -> None:
    _, dispatcher, handler = handler_setup
    received: list[StatisticalTestCompletedEvent] = []

    dispatcher.subscribe(StatisticalTestCompletedEvent, received.append)

    result = handler.handle(
        RunStatisticalTestCommand(
            method=StatisticalTestMethod.MANN_KENDALL,
            series_ids=("handler_temperature",),
        )
    )

    assert result.significant is True
    assert len(received) == 1
    assert received[0].result == result


def test_handler_publishes_failed_event_for_missing_series(
    handler_setup,
) -> None:
    _, dispatcher, handler = handler_setup
    received: list[StatisticalTestFailedEvent] = []

    dispatcher.subscribe(StatisticalTestFailedEvent, received.append)

    with pytest.raises(StatisticalTestingError):
        handler.handle(
            RunStatisticalTestCommand(
                method=StatisticalTestMethod.MANN_KENDALL,
                series_ids=("missing_temperature",),
            )
        )

    assert len(received) == 1
    assert received[0].series_ids == ("missing_temperature",)


def test_handler_rejects_invalid_command(handler_setup) -> None:
    _, _, handler = handler_setup

    with pytest.raises(TypeError, match="RunStatisticalTestCommand"):
        handler.handle("invalid")  # type: ignore[arg-type]
