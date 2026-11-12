"""Tests for the trend analysis command handler."""

from datetime import UTC, datetime, timedelta

import pytest

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.time_series_management import (
    TimeSeriesManager,
)
from earth_twin_engine.application.modules.trend_analysis import (
    AnalyzeTimeSeriesTrendCommand,
    TrendAnalysisCompletedEvent,
    TrendAnalysisFailedEvent,
    TrendAnalysisHandler,
    TrendAnalyzer,
    TrendDirection,
    TrendSeriesNotFoundError,
)
from earth_twin_engine.domain.geography import SpatialCoordinate
from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import TimeSeries, TimeSeriesPoint
from earth_twin_engine.domain.variables import (
    EarthVariable,
    VariableCategory,
    VariableMetadata,
)


@pytest.fixture
def registered_series() -> TimeSeries:
    variable = EarthVariable(
        variable_id="rainfall",
        name="Rainfall",
        description="Daily rainfall.",
        category=next(iter(VariableCategory)),
        metadata=VariableMetadata(
            unit="mm",
            temporal_resolutions=(TemporalResolution.DAILY,),
        ),
    )

    start = datetime(2025, 1, 1, tzinfo=UTC)
    points = tuple(
        TimeSeriesPoint(
            timestamp=start + timedelta(days=index),
            value=float(index * 5),
        )
        for index in range(6)
    )

    return TimeSeries(
        series_id="rainfall_series",
        variable=variable,
        location=SpatialCoordinate(latitude=20.0, longitude=78.0),
        temporal_resolution=TemporalResolution.DAILY,
        points=points,
    )


def test_handler_publishes_completed_event(
    registered_series: TimeSeries,
) -> None:
    manager = TimeSeriesManager()
    manager.register(registered_series)

    dispatcher = EventDispatcher()
    received_events: list[TrendAnalysisCompletedEvent] = []
    dispatcher.subscribe(
        TrendAnalysisCompletedEvent,
        received_events.append,
    )

    handler = TrendAnalysisHandler(
        manager=manager,
        analyzer=TrendAnalyzer(),
        event_dispatcher=dispatcher,
    )

    result = handler.handle(AnalyzeTimeSeriesTrendCommand(series_id="rainfall_series"))

    assert result.direction == TrendDirection.INCREASING
    assert len(received_events) == 1
    assert received_events[0].result == result


def test_handler_publishes_failed_event_for_unknown_series() -> None:
    manager = TimeSeriesManager()
    dispatcher = EventDispatcher()
    received_events: list[TrendAnalysisFailedEvent] = []

    dispatcher.subscribe(
        TrendAnalysisFailedEvent,
        received_events.append,
    )

    handler = TrendAnalysisHandler(
        manager=manager,
        analyzer=TrendAnalyzer(),
        event_dispatcher=dispatcher,
    )

    with pytest.raises(TrendSeriesNotFoundError):
        handler.handle(AnalyzeTimeSeriesTrendCommand(series_id="missing-series"))

    assert len(received_events) == 1
    assert received_events[0].series_id == "missing-series"


def test_handler_rejects_invalid_command() -> None:
    handler = TrendAnalysisHandler(
        manager=TimeSeriesManager(),
        analyzer=TrendAnalyzer(),
        event_dispatcher=EventDispatcher(),
    )

    with pytest.raises(TypeError, match="AnalyzeTimeSeriesTrendCommand"):
        handler.handle("invalid")  # type: ignore[arg-type]
