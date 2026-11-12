"""Tests for the DataValidationHandler."""

from uuid import uuid4

import pytest

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.data_validation import (
    DatasetValidator,
    DataValidationHandler,
)
from earth_twin_engine.application.modules.data_validation.commands import (
    ValidateDatasetCommand,
)
from earth_twin_engine.application.modules.data_validation.events import (
    DatasetValidatedEvent,
)


@pytest.fixture
def event_dispatcher() -> EventDispatcher:
    return EventDispatcher()


@pytest.fixture
def validator() -> DatasetValidator:
    return DatasetValidator()


@pytest.fixture
def handler(validator, event_dispatcher) -> DataValidationHandler:
    return DataValidationHandler(
        validator=validator,
        event_dispatcher=event_dispatcher,
    )


def test_handle_returns_validation_result(
    handler,
    dataset,
    valid_time_series_collection,
) -> None:
    command = ValidateDatasetCommand(
        dataset=dataset,
        time_series=valid_time_series_collection,
    )

    result = handler.handle(command)

    assert result.dataset_id == dataset.dataset_id
    assert result.is_valid
    assert result.checked_series_count == 1
    assert result.observation_count == 3


def test_handle_publishes_validation_event(
    handler,
    event_dispatcher,
    dataset,
    valid_time_series_collection,
) -> None:
    received_events = []

    event_dispatcher.subscribe(
        DatasetValidatedEvent,
        received_events.append,
    )

    command = ValidateDatasetCommand(
        dataset=dataset,
        time_series=valid_time_series_collection,
    )

    result = handler.handle(command)

    assert len(received_events) == 1

    event = received_events[0]

    assert event.dataset_id == dataset.dataset_id
    assert event.command_id == command.command_id
    assert event.correlation_id == command.correlation_id
    assert event.validation_result is result


def test_handle_preserves_correlation_id(
    handler,
    event_dispatcher,
    dataset,
    valid_time_series_collection,
) -> None:
    received_events = []

    event_dispatcher.subscribe(
        DatasetValidatedEvent,
        received_events.append,
    )

    correlation_id = uuid4()

    command = ValidateDatasetCommand(
        dataset=dataset,
        time_series=valid_time_series_collection,
        correlation_id=correlation_id,
    )

    handler.handle(command)

    assert received_events[0].correlation_id == correlation_id


def test_handle_publishes_event_for_invalid_dataset(
    handler,
    event_dispatcher,
    dataset,
) -> None:
    received_events = []

    event_dispatcher.subscribe(
        DatasetValidatedEvent,
        received_events.append,
    )

    command = ValidateDatasetCommand(
        dataset=dataset,
        time_series=(),
    )

    result = handler.handle(command)

    assert not result.is_valid
    assert len(received_events) == 1
    assert received_events[0].validation_result is result


def test_handle_rejects_invalid_command(handler) -> None:
    with pytest.raises(TypeError, match="ValidateDatasetCommand"):
        handler.handle(None)


def test_constructor_rejects_invalid_validator(event_dispatcher) -> None:
    with pytest.raises(TypeError, match="DatasetValidator"):
        DataValidationHandler(
            validator=None,
            event_dispatcher=event_dispatcher,
        )


def test_constructor_rejects_invalid_event_dispatcher(validator) -> None:
    with pytest.raises(TypeError, match="EventDispatcher"):
        DataValidationHandler(
            validator=validator,
            event_dispatcher=None,
        )
