"""Tests for regional comparison commands and events."""

from uuid import uuid4

import pytest

from earth_twin_engine.application.modules.regional_comparison import (
    CompareRegionsCommand,
    RegionalComparisonCompletedEvent,
    RegionalComparisonFailedEvent,
)


def test_command_accepts_valid_request() -> None:
    command = CompareRegionsCommand(
        region_ids=("region_north", "region_south"),
        variable_id="surface_temperature",
    )

    assert command.region_ids == ("region_north", "region_south")
    assert command.variable_id == "surface_temperature"
    assert command.command_id is not None


@pytest.mark.parametrize(
    ("region_ids", "variable_id"),
    [
        ((), "surface_temperature"),
        (("region_north",), "surface_temperature"),
        (("region_north", "region_north"), "surface_temperature"),
        (("region_north", ""), "surface_temperature"),
        (("region_north", "region_south"), ""),
        (("region_north", "region_south"), " "),
    ],
)
def test_command_rejects_invalid_request(
    region_ids,
    variable_id,
) -> None:
    from earth_twin_engine.application.modules.regional_comparison.errors import (
        InvalidRegionalComparisonError,
    )

    with pytest.raises(InvalidRegionalComparisonError):
        CompareRegionsCommand(
            region_ids=region_ids,
            variable_id=variable_id,
        )


def test_completed_event_accepts_valid_payload(service) -> None:
    result = service.compare(
        ("region_north", "region_south"),
        "surface_temperature",
    )
    command_id = uuid4()
    correlation_id = uuid4()

    event = RegionalComparisonCompletedEvent(
        command_id=command_id,
        correlation_id=correlation_id,
        result=result,
    )

    assert event.command_id == command_id
    assert event.correlation_id == correlation_id
    assert event.result is result


def test_completed_event_accepts_missing_correlation_id(service) -> None:
    result = service.compare(
        ("region_north", "region_south"),
        "surface_temperature",
    )

    event = RegionalComparisonCompletedEvent(
        command_id=uuid4(),
        correlation_id=None,
        result=result,
    )

    assert event.correlation_id is None


def test_completed_event_rejects_invalid_command_id(service) -> None:
    result = service.compare(
        ("region_north", "region_south"),
        "surface_temperature",
    )

    with pytest.raises(TypeError, match="command_id"):
        RegionalComparisonCompletedEvent(
            command_id="invalid",  # type: ignore[arg-type]
            correlation_id=None,
            result=result,
        )


def test_completed_event_rejects_invalid_correlation_id(service) -> None:
    result = service.compare(
        ("region_north", "region_south"),
        "surface_temperature",
    )

    with pytest.raises(TypeError, match="correlation_id"):
        RegionalComparisonCompletedEvent(
            command_id=uuid4(),
            correlation_id="invalid",  # type: ignore[arg-type]
            result=result,
        )


def test_completed_event_rejects_invalid_result() -> None:
    with pytest.raises(TypeError, match="RegionalComparisonResult"):
        RegionalComparisonCompletedEvent(
            command_id=uuid4(),
            correlation_id=None,
            result=None,  # type: ignore[arg-type]
        )


def test_failed_event_accepts_valid_payload() -> None:
    command_id = uuid4()
    correlation_id = uuid4()

    event = RegionalComparisonFailedEvent(
        command_id=command_id,
        correlation_id=correlation_id,
        variable_id="surface_temperature",
        region_ids=("region_north", "region_south"),
        error_type="RegionalComparisonDataError",
        error_message="No matching time series.",
    )

    assert event.command_id == command_id
    assert event.correlation_id == correlation_id
    assert event.variable_id == "surface_temperature"
    assert event.region_ids == ("region_north", "region_south")
    assert event.error_type == "RegionalComparisonDataError"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("variable_id", ""),
        ("variable_id", " "),
        ("error_type", ""),
        ("error_type", " "),
        ("error_message", ""),
        ("error_message", " "),
    ],
)
def test_failed_event_rejects_empty_text_fields(
    field,
    value,
) -> None:
    values = {
        "command_id": uuid4(),
        "correlation_id": None,
        "variable_id": "surface_temperature",
        "region_ids": ("region_north", "region_south"),
        "error_type": "RuntimeError",
        "error_message": "Comparison failed.",
    }
    values[field] = value

    with pytest.raises(ValueError, match=field):
        RegionalComparisonFailedEvent(**values)


def test_failed_event_rejects_invalid_region_ids() -> None:
    with pytest.raises(ValueError, match="region_ids"):
        RegionalComparisonFailedEvent(
            command_id=uuid4(),
            correlation_id=None,
            variable_id="surface_temperature",
            region_ids=(),  # type: ignore[arg-type]
            error_type="RuntimeError",
            error_message="Comparison failed.",
        )


def test_failed_event_rejects_invalid_command_id() -> None:
    with pytest.raises(TypeError, match="command_id"):
        RegionalComparisonFailedEvent(
            command_id="invalid",  # type: ignore[arg-type]
            correlation_id=None,
            variable_id="surface_temperature",
            region_ids=("region_north", "region_south"),
            error_type="RuntimeError",
            error_message="Comparison failed.",
        )
