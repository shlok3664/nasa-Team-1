"""Tests for DataNormalizationHandler."""

from uuid import uuid4

import pytest

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.data_normalization import (
    DataNormalizationHandler,
    DataNormalizer,
)
from earth_twin_engine.application.modules.data_normalization.commands import (
    NormalizeDatasetCommand,
)
from earth_twin_engine.application.modules.data_normalization.events import (
    DatasetNormalizedEvent,
)


@pytest.fixture
def event_dispatcher() -> EventDispatcher:
    return EventDispatcher()


@pytest.fixture
def handler(event_dispatcher) -> DataNormalizationHandler:
    return DataNormalizationHandler(
        normalizer=DataNormalizer(),
        event_dispatcher=event_dispatcher,
    )


def test_handler_returns_normalization_result(
    handler,
    dataset,
    celsius_series_collection,
) -> None:
    command = NormalizeDatasetCommand(
        dataset=dataset,
        time_series=celsius_series_collection,
    )

    result = handler.handle(command)

    assert result.dataset.dataset_id.endswith("_normalized")
    assert result.time_series[0].points[0].value == pytest.approx(285.4)


def test_handler_publishes_normalized_event(
    handler,
    event_dispatcher,
    dataset,
    celsius_series_collection,
) -> None:
    events = []
    event_dispatcher.subscribe(DatasetNormalizedEvent, events.append)

    command = NormalizeDatasetCommand(
        dataset=dataset,
        time_series=celsius_series_collection,
    )

    result = handler.handle(command)

    assert len(events) == 1
    assert events[0].command_id == command.command_id
    assert events[0].correlation_id == command.correlation_id
    assert events[0].dataset_id == result.dataset.dataset_id
    assert events[0].normalization_result is result


def test_handler_preserves_correlation_id(
    handler,
    event_dispatcher,
    dataset,
    celsius_series_collection,
) -> None:
    events = []
    event_dispatcher.subscribe(DatasetNormalizedEvent, events.append)

    correlation_id = uuid4()

    command = NormalizeDatasetCommand(
        dataset=dataset,
        time_series=celsius_series_collection,
        correlation_id=correlation_id,
    )

    handler.handle(command)

    assert events[0].correlation_id == correlation_id


def test_handler_rejects_invalid_command(handler) -> None:
    with pytest.raises(TypeError, match="NormalizeDatasetCommand"):
        handler.handle(None)


def test_handler_rejects_invalid_normalizer(event_dispatcher) -> None:
    with pytest.raises(TypeError, match="DataNormalizer"):
        DataNormalizationHandler(
            normalizer=None,
            event_dispatcher=event_dispatcher,
        )


def test_handler_rejects_invalid_event_dispatcher() -> None:
    with pytest.raises(TypeError, match="EventDispatcher"):
        DataNormalizationHandler(
            normalizer=DataNormalizer(),
            event_dispatcher=None,
        )
