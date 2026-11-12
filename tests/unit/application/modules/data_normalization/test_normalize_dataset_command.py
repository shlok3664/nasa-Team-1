"""Tests for NormalizeDatasetCommand."""

import pytest

from earth_twin_engine.application.modules.data_normalization.commands import (
    NormalizeDatasetCommand,
)


def test_command_constructs_successfully(dataset, celsius_series_collection) -> None:
    command = NormalizeDatasetCommand(
        dataset=dataset,
        time_series=celsius_series_collection,
    )

    assert command.dataset is dataset
    assert command.time_series == celsius_series_collection
    assert command.command_id is not None


def test_command_rejects_invalid_dataset(celsius_series_collection) -> None:
    with pytest.raises(TypeError, match="dataset"):
        NormalizeDatasetCommand(
            dataset=None,
            time_series=celsius_series_collection,
        )


def test_command_rejects_non_tuple_time_series(dataset) -> None:
    with pytest.raises(TypeError, match="tuple"):
        NormalizeDatasetCommand(dataset=dataset, time_series=[])


def test_command_rejects_invalid_series_member(dataset) -> None:
    with pytest.raises(TypeError, match="TimeSeries"):
        NormalizeDatasetCommand(dataset=dataset, time_series=("invalid",))


def test_command_accepts_empty_series(dataset) -> None:
    command = NormalizeDatasetCommand(dataset=dataset, time_series=())

    assert command.time_series == ()
