"""Tests for Data Acquisition commands and events."""

from uuid import uuid4

import pytest

from earth_twin_engine.application.modules.data_acquisition.commands import (
    AcquireDatasetCommand,
)
from earth_twin_engine.application.modules.data_acquisition.events import (
    DatasetAcquiredEvent,
    DatasetAcquisitionFailedEvent,
)
from earth_twin_engine.domain.temporal import TemporalResolution


def make_command(temporal_range) -> AcquireDatasetCommand:
    return AcquireDatasetCommand(
        variable_id="air_temperature",
        region_id="india",
        temporal_range=temporal_range,
        temporal_resolution=TemporalResolution.DAILY,
    )


def test_create_acquire_dataset_command(temporal_range) -> None:
    command = make_command(temporal_range)

    assert command.variable_id == "air_temperature"
    assert command.region_id == "india"
    assert command.temporal_range == temporal_range
    assert command.temporal_resolution is TemporalResolution.DAILY
    assert command.source_id is None
    assert command.command_id is not None
    assert command.issued_at is not None


@pytest.mark.parametrize("value", ["", " ", "\t"])
def test_reject_empty_variable_id(value, temporal_range) -> None:
    with pytest.raises(ValueError, match="variable_id"):
        AcquireDatasetCommand(
            variable_id=value,
            region_id="india",
            temporal_range=temporal_range,
            temporal_resolution=TemporalResolution.DAILY,
        )


@pytest.mark.parametrize("value", ["", " ", "\t"])
def test_reject_empty_region_id(value, temporal_range) -> None:
    with pytest.raises(ValueError, match="region_id"):
        AcquireDatasetCommand(
            variable_id="air_temperature",
            region_id=value,
            temporal_range=temporal_range,
            temporal_resolution=TemporalResolution.DAILY,
        )


@pytest.mark.parametrize("field_name", ["variable_id", "region_id"])
def test_reject_non_string_identifiers(field_name, temporal_range) -> None:
    values = {
        "variable_id": "air_temperature",
        "region_id": "india",
        "temporal_range": temporal_range,
        "temporal_resolution": TemporalResolution.DAILY,
    }
    values[field_name] = 123

    with pytest.raises(TypeError):
        AcquireDatasetCommand(**values)


def test_reject_invalid_temporal_range() -> None:
    with pytest.raises(TypeError, match="temporal_range"):
        AcquireDatasetCommand(
            variable_id="air_temperature",
            region_id="india",
            temporal_range="invalid",  # type: ignore[arg-type]
            temporal_resolution=TemporalResolution.DAILY,
        )


def test_reject_invalid_temporal_resolution(temporal_range) -> None:
    with pytest.raises(TypeError, match="temporal_resolution"):
        AcquireDatasetCommand(
            variable_id="air_temperature",
            region_id="india",
            temporal_range=temporal_range,
            temporal_resolution="daily",  # type: ignore[arg-type]
        )


def test_reject_invalid_source_id(temporal_range) -> None:
    with pytest.raises(ValueError, match="source_id"):
        AcquireDatasetCommand(
            variable_id="air_temperature",
            region_id="india",
            temporal_range=temporal_range,
            temporal_resolution=TemporalResolution.DAILY,
            source_id=" ",
        )


def test_reject_non_string_source_id(temporal_range) -> None:
    with pytest.raises(TypeError, match="source_id"):
        AcquireDatasetCommand(
            variable_id="air_temperature",
            region_id="india",
            temporal_range=temporal_range,
            temporal_resolution=TemporalResolution.DAILY,
            source_id=123,  # type: ignore[arg-type]
        )


def test_create_dataset_acquired_event(dataset) -> None:
    command_id = uuid4()

    event = DatasetAcquiredEvent(
        command_id=command_id,
        dataset=dataset,
    )

    assert event.command_id == command_id
    assert event.dataset is dataset
    assert event.event_id is not None
    assert event.occurred_at is not None


def test_reject_invalid_acquired_event_command_id(dataset) -> None:
    with pytest.raises(TypeError, match="command_id"):
        DatasetAcquiredEvent(
            command_id="invalid",  # type: ignore[arg-type]
            dataset=dataset,
        )


def test_reject_invalid_acquired_event_dataset() -> None:
    with pytest.raises(TypeError, match="dataset"):
        DatasetAcquiredEvent(
            command_id=uuid4(),
            dataset=object(),  # type: ignore[arg-type]
        )


def test_create_dataset_acquisition_failed_event() -> None:
    command_id = uuid4()
    exception = RuntimeError("Source unavailable")

    event = DatasetAcquisitionFailedEvent(
        command_id=command_id,
        variable_id="air_temperature",
        region_id="india",
        exception=exception,
    )

    assert event.command_id == command_id
    assert event.variable_id == "air_temperature"
    assert event.region_id == "india"
    assert event.exception is exception


def test_reject_invalid_failed_event_exception() -> None:
    with pytest.raises(TypeError, match="exception"):
        DatasetAcquisitionFailedEvent(
            command_id=uuid4(),
            variable_id="air_temperature",
            region_id="india",
            exception="not an exception",  # type: ignore[arg-type]
        )
