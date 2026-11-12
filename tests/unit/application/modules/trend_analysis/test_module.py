"""Tests for the trend analysis application module."""

import pytest

from earth_twin_engine.application.modules.trend_analysis import (
    TrendAnalysisModule,
    TrendAnalyzer,
)


def test_module_exposes_metadata() -> None:
    module = TrendAnalysisModule()

    assert module.metadata.module_id == "trend_analysis"
    assert module.metadata.name == "Trend Analysis"
    assert module.metadata.version == "1.0.0"
    assert module.metadata.dependencies == ("time_series_management",)


def test_module_starts_uninitialized() -> None:
    module = TrendAnalysisModule()

    assert module.is_initialized is False
    assert module.is_running is False
    assert isinstance(module.analyzer, TrendAnalyzer)
    assert module.handler is None


def test_module_rejects_start_before_initialization() -> None:
    module = TrendAnalysisModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.start()


def test_module_rejects_update_before_initialization() -> None:
    module = TrendAnalysisModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.update(0.1)


def test_module_can_shutdown_before_initialization() -> None:
    module = TrendAnalysisModule()

    module.shutdown()

    assert module.is_initialized is False
    assert module.is_running is False


def test_module_rejects_invalid_significance_level() -> None:
    with pytest.raises(ValueError):
        TrendAnalysisModule(significance_level=2.0)
