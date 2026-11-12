"""Tests for the ValidateDatasetCommand."""

import pytest

from earth_twin_engine.application.modules.data_validation.commands import (
    ValidateDatasetCommand,
)


def test_constructor_creates_command(dataset, valid_time_series_collection) -> None:
    command = ValidateDatasetCommand(
        dataset=dataset,
        time_series=valid_time_series_collection,
    )

    assert command.dataset is dataset
    assert command.time_series == valid_time_series_collection
    assert command.command_id is not None


def test_constructor_rejects_invalid_dataset(valid_time_series_collection) -> None:
    with pytest.raises(TypeError, match="dataset"):
        ValidateDatasetCommand(
            dataset=None,
            time_series=valid_time_series_collection,
        )


def test_constructor_rejects_non_tuple_time_series(dataset) -> None:
    with pytest.raises(TypeError, match="tuple"):
        ValidateDatasetCommand(
            dataset=dataset,
            time_series=[],
        )


def test_constructor_rejects_invalid_time_series_member(dataset) -> None:
    with pytest.raises(TypeError, match="TimeSeries"):
        ValidateDatasetCommand(
            dataset=dataset,
            time_series=("invalid",),
        )


def test_constructor_accepts_empty_time_series(dataset) -> None:
    command = ValidateDatasetCommand(
        dataset=dataset,
        time_series=(),
    )

    assert command.time_series == ()
