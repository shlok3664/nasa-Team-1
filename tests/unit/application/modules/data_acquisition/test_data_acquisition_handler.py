"""Tests for the Data Acquisition command handler."""

from uuid import uuid4

import pytest

from earth_twin_engine.application.modules.data_acquisition.commands import (
    AcquireDatasetCommand,
)
from earth_twin_engine.application.modules.data_acquisition.events import (
    DatasetAcquiredEvent,
    DatasetAcquisitionFailedEvent,
)
from earth_twin_engine.domain.datasets import DataRequest
from earth_twin_engine.domain.temporal import TemporalResolution


def make_command(temporal_range, **overrides) -> AcquireDatasetCommand:
    values = {
        "variable_id": "air_temperature",
        "region_id": "india",
        "temporal_range": temporal_range,
        "temporal_resolution": TemporalResolution.DAILY,
    }
    values.update(overrides)
    return AcquireDatasetCommand(**values)


def test_handler_acquires_dataset(
    acquisition_handler,
    temporal_range,
    dataset,
    data_source_manager,
    event_dispatcher,
) -> None:
    events = []
    event_dispatcher.subscribe(DatasetAcquiredEvent, events.append)

    command = make_command(temporal_range)

    result = acquisition_handler.handle(command)

    assert result is dataset
    assert len(events) == 1
    assert events[0].dataset is dataset
    assert events[0].command_id == command.command_id
    assert events[0].correlation_id == command.correlation_id

    adapter = data_source_manager.get_adapter("nasa_merra2")
    adapter.retrieve.assert_called_once()

    request = adapter.retrieve.call_args.args[0]
    assert isinstance(request, DataRequest)
    assert request.variable.variable_id == "air_temperature"
    assert request.region.region_id == "india"
    assert request.temporal_range == temporal_range
    assert request.temporal_resolution is TemporalResolution.DAILY


def test_handler_propagates_correlation_id(
    acquisition_handler,
    temporal_range,
    event_dispatcher,
) -> None:
    events = []
    event_dispatcher.subscribe(DatasetAcquiredEvent, events.append)

    correlation_id = uuid4()
    command = make_command(
        temporal_range,
        correlation_id=correlation_id,
    )

    acquisition_handler.handle(command)

    assert events[0].correlation_id == correlation_id


def test_handler_publishes_failure_for_unknown_variable(
    acquisition_handler,
    temporal_range,
    event_dispatcher,
) -> None:
    events = []
    event_dispatcher.subscribe(DatasetAcquisitionFailedEvent, events.append)

    command = make_command(
        temporal_range,
        variable_id="unknown_variable",
    )

    with pytest.raises(KeyError):
        acquisition_handler.handle(command)

    assert len(events) == 1
    assert events[0].command_id == command.command_id
    assert events[0].variable_id == "unknown_variable"
    assert isinstance(events[0].exception, KeyError)


def test_handler_publishes_failure_for_unknown_region(
    acquisition_handler,
    temporal_range,
    event_dispatcher,
) -> None:
    events = []
    event_dispatcher.subscribe(DatasetAcquisitionFailedEvent, events.append)

    command = make_command(
        temporal_range,
        region_id="unknown_region",
    )

    with pytest.raises(Exception, match="not registered"):
        acquisition_handler.handle(command)

    assert len(events) == 1
    assert events[0].region_id == "unknown_region"


def test_handler_publishes_failure_for_invalid_temporal_resolution(
    acquisition_handler,
    temporal_range,
    event_dispatcher,
) -> None:
    events = []
    event_dispatcher.subscribe(DatasetAcquisitionFailedEvent, events.append)

    command = make_command(
        temporal_range,
        temporal_resolution=TemporalResolution.MONTHLY,
    )

    with pytest.raises(ValueError):
        acquisition_handler.handle(command)

    assert len(events) == 1
    assert isinstance(events[0].exception, ValueError)


def test_handler_publishes_failure_when_source_retrieval_fails(
    acquisition_handler,
    temporal_range,
    data_source_manager,
    event_dispatcher,
) -> None:
    events = []
    event_dispatcher.subscribe(DatasetAcquisitionFailedEvent, events.append)

    adapter = data_source_manager.get_adapter("nasa_merra2")
    adapter.retrieve.side_effect = RuntimeError("Remote source failed")

    command = make_command(temporal_range)

    with pytest.raises(RuntimeError, match="Remote source failed"):
        acquisition_handler.handle(command)

    assert len(events) == 1
    assert isinstance(events[0].exception, RuntimeError)


def test_handler_rejects_invalid_command(acquisition_handler) -> None:
    with pytest.raises(TypeError, match="AcquireDatasetCommand"):
        acquisition_handler.handle(object())  # type: ignore[arg-type]


def test_successful_acquisition_survives_event_subscriber_failure(
    acquisition_handler,
    temporal_range,
    event_dispatcher,
    dataset,
) -> None:
    def failing_subscriber(event: DatasetAcquiredEvent) -> None:
        raise RuntimeError("Subscriber failed")

    event_dispatcher.subscribe(DatasetAcquiredEvent, failing_subscriber)

    command = make_command(temporal_range)

    result = acquisition_handler.handle(command)

    assert result is dataset
