"""Tests for time-series management module metadata and lifecycle state."""

import pytest

from earth_twin_engine.application.modules.time_series_management import (
    TimeSeriesManagementModule,
)


def test_module_metadata() -> None:
    module = TimeSeriesManagementModule()

    assert module.metadata.module_id == "time_series_management"
    assert module.metadata.name == "Time-Series Management"
    assert module.metadata.version == "1.0.0"
    assert "data_normalization" in module.metadata.dependencies


def test_module_starts_uninitialized() -> None:
    module = TimeSeriesManagementModule()

    assert module.is_initialized is False
    assert module.is_running is False


def test_manager_requires_initialization() -> None:
    module = TimeSeriesManagementModule()

    with pytest.raises(RuntimeError, match="not initialized"):
        _ = module.manager


def test_start_requires_initialization() -> None:
    module = TimeSeriesManagementModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.start()


def test_update_requires_initialization() -> None:
    module = TimeSeriesManagementModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.update(0.1)
