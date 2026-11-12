"""Tests for the statistical testing application module."""

import pytest

from earth_twin_engine.application.modules.statistical_testing import (
    StatisticalTestingModule,
    StatisticalTestMethod,
)


def test_module_exposes_metadata() -> None:
    module = StatisticalTestingModule()

    assert module.metadata.module_id == "statistical_testing"
    assert module.metadata.name == "Statistical Testing"
    assert module.metadata.version == "1.0.0"
    assert module.metadata.dependencies == ("time_series_management",)


def test_module_registers_all_default_tests() -> None:
    module = StatisticalTestingModule()

    assert set(module.registry.get_all()) == {
        StatisticalTestMethod.MANN_KENDALL,
        StatisticalTestMethod.ONE_SAMPLE_T,
        StatisticalTestMethod.WELCH_T,
    }


def test_module_starts_uninitialized() -> None:
    module = StatisticalTestingModule()

    assert module.is_initialized is False
    assert module.is_running is False
    assert module.handler is None


def test_module_rejects_start_before_initialization() -> None:
    module = StatisticalTestingModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.start()


def test_module_rejects_update_before_initialization() -> None:
    module = StatisticalTestingModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.update(0.1)


def test_module_can_shutdown_before_initialization() -> None:
    module = StatisticalTestingModule()

    module.shutdown()

    assert module.is_initialized is False
    assert module.is_running is False


@pytest.mark.parametrize("significance_level", [0.0, 1.0, -0.1, 1.1, float("nan")])
def test_module_rejects_invalid_significance_level(
    significance_level: float,
) -> None:
    with pytest.raises(ValueError):
        StatisticalTestingModule(significance_level=significance_level)
