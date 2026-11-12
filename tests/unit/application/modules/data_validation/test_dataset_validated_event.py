"""Tests for the DatasetValidatedEvent."""

from uuid import uuid4

import pytest

from earth_twin_engine.application.modules.data_validation.events import (
    DatasetValidatedEvent,
)
from earth_twin_engine.application.modules.data_validation.validation_result import (
    ValidationResult,
)


@pytest.fixture
def validation_result() -> ValidationResult:
    return ValidationResult(
        dataset_id="india_daily_temperature",
        issues=(),
        checked_series_count=1,
        observation_count=3,
        valid_observation_count=3,
        missing_observation_count=0,
    )


def test_constructor_creates_event(validation_result) -> None:
    command_id = uuid4()
    correlation_id = uuid4()

    event = DatasetValidatedEvent(
        command_id=command_id,
        correlation_id=correlation_id,
        dataset_id="india_daily_temperature",
        validation_result=validation_result,
    )

    assert event.command_id == command_id
    assert event.correlation_id == correlation_id
    assert event.dataset_id == "india_daily_temperature"
    assert event.validation_result is validation_result


def test_constructor_accepts_missing_correlation_id(validation_result) -> None:
    event = DatasetValidatedEvent(
        command_id=uuid4(),
        dataset_id="india_daily_temperature",
        validation_result=validation_result,
    )

    assert event.correlation_id is None


def test_constructor_rejects_invalid_command_id(validation_result) -> None:
    with pytest.raises(TypeError, match="command_id"):
        DatasetValidatedEvent(
            command_id="invalid",
            dataset_id="india_daily_temperature",
            validation_result=validation_result,
        )


def test_constructor_rejects_invalid_correlation_id(validation_result) -> None:
    with pytest.raises(TypeError, match="correlation_id"):
        DatasetValidatedEvent(
            command_id=uuid4(),
            correlation_id="invalid",
            dataset_id="india_daily_temperature",
            validation_result=validation_result,
        )


@pytest.mark.parametrize("dataset_id", ["", " ", None])
def test_constructor_rejects_invalid_dataset_id(
    validation_result,
    dataset_id,
) -> None:
    with pytest.raises(ValueError, match="dataset_id"):
        DatasetValidatedEvent(
            command_id=uuid4(),
            dataset_id=dataset_id,
            validation_result=validation_result,
        )


def test_constructor_rejects_invalid_validation_result() -> None:
    with pytest.raises(TypeError, match="ValidationResult"):
        DatasetValidatedEvent(
            command_id=uuid4(),
            dataset_id="india_daily_temperature",
            validation_result=None,
        )
