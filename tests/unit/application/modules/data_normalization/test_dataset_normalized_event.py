"""Tests for DatasetNormalizedEvent."""

from uuid import uuid4

import pytest

from earth_twin_engine.application.modules.data_normalization.events import (
    DatasetNormalizedEvent,
)
from earth_twin_engine.application.modules.data_normalization.normalization_result import (
    NormalizationResult,
)


@pytest.fixture
def normalization_result(dataset) -> NormalizationResult:
    return NormalizationResult(
        dataset=dataset,
        time_series=(),
        transformations=("Timestamps converted to UTC.",),
    )


def test_event_constructs_successfully(normalization_result) -> None:
    command_id = uuid4()
    correlation_id = uuid4()

    event = DatasetNormalizedEvent(
        command_id=command_id,
        correlation_id=correlation_id,
        dataset_id="india_daily_temperature_normalized",
        normalization_result=normalization_result,
    )

    assert event.command_id == command_id
    assert event.correlation_id == correlation_id
    assert event.normalization_result is normalization_result


def test_event_accepts_missing_correlation_id(normalization_result) -> None:
    event = DatasetNormalizedEvent(
        command_id=uuid4(),
        dataset_id="india_daily_temperature_normalized",
        normalization_result=normalization_result,
    )

    assert event.correlation_id is None


def test_event_rejects_invalid_command_id(normalization_result) -> None:
    with pytest.raises(TypeError, match="command_id"):
        DatasetNormalizedEvent(
            command_id="invalid",
            dataset_id="normalized",
            normalization_result=normalization_result,
        )


def test_event_rejects_invalid_correlation_id(normalization_result) -> None:
    with pytest.raises(TypeError, match="correlation_id"):
        DatasetNormalizedEvent(
            command_id=uuid4(),
            correlation_id="invalid",
            dataset_id="normalized",
            normalization_result=normalization_result,
        )


@pytest.mark.parametrize("dataset_id", ["", " ", None])
def test_event_rejects_invalid_dataset_id(
    normalization_result,
    dataset_id,
) -> None:
    with pytest.raises(ValueError, match="dataset_id"):
        DatasetNormalizedEvent(
            command_id=uuid4(),
            dataset_id=dataset_id,
            normalization_result=normalization_result,
        )


def test_event_rejects_invalid_result() -> None:
    with pytest.raises(TypeError, match="NormalizationResult"):
        DatasetNormalizedEvent(
            command_id=uuid4(),
            dataset_id="normalized",
            normalization_result=None,
        )
