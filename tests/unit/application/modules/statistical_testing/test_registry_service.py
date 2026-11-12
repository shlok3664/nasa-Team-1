"""Tests for statistical test registration and execution service."""

import pytest

from earth_twin_engine.application.modules.statistical_testing import (
    DuplicateStatisticalTestError,
    MannKendallTest,
    OneSampleTTest,
    StatisticalTestingService,
    StatisticalTestMethod,
    StatisticalTestNotFoundError,
    StatisticalTestRegistry,
    WelchTTest,
)


def test_registry_registers_supported_tests() -> None:
    registry = StatisticalTestRegistry()

    registry.register(MannKendallTest())
    registry.register(OneSampleTTest())
    registry.register(WelchTTest())

    assert registry.count == 3
    assert set(registry.get_all()) == {
        StatisticalTestMethod.MANN_KENDALL,
        StatisticalTestMethod.ONE_SAMPLE_T,
        StatisticalTestMethod.WELCH_T,
    }


def test_registry_rejects_duplicate_test() -> None:
    registry = StatisticalTestRegistry()
    registry.register(MannKendallTest())

    with pytest.raises(DuplicateStatisticalTestError):
        registry.register(MannKendallTest())


def test_registry_resolves_test() -> None:
    registry = StatisticalTestRegistry()
    test = MannKendallTest()
    registry.register(test)

    assert registry.get(StatisticalTestMethod.MANN_KENDALL) is test


def test_registry_rejects_unknown_test() -> None:
    registry = StatisticalTestRegistry()

    with pytest.raises(StatisticalTestNotFoundError):
        registry.get(StatisticalTestMethod.MANN_KENDALL)


def test_registry_unregisters_test() -> None:
    registry = StatisticalTestRegistry()
    registry.register(MannKendallTest())

    assert registry.unregister(StatisticalTestMethod.MANN_KENDALL) is True
    assert registry.unregister(StatisticalTestMethod.MANN_KENDALL) is False
    assert registry.count == 0


def test_service_executes_registered_test(make_series) -> None:
    registry = StatisticalTestRegistry()
    registry.register(MannKendallTest())
    service = StatisticalTestingService(registry)

    series = make_series("service_temperature", [10.0, 12.0, 14.0, 16.0])

    result = service.run(
        method=StatisticalTestMethod.MANN_KENDALL,
        series=(series,),
    )

    assert result.method == StatisticalTestMethod.MANN_KENDALL
    assert result.series_ids == ("service_temperature",)


def test_service_rejects_invalid_series_argument() -> None:
    service = StatisticalTestingService(StatisticalTestRegistry())

    with pytest.raises(ValueError, match="non-empty tuple"):
        service.run(
            method=StatisticalTestMethod.MANN_KENDALL,
            series=(),  # type: ignore[arg-type]
        )


def test_service_rejects_invalid_significance_level(make_series) -> None:
    registry = StatisticalTestRegistry()
    registry.register(MannKendallTest())
    service = StatisticalTestingService(registry)

    series = make_series("invalid_alpha_temperature", [1.0, 2.0, 3.0])

    with pytest.raises(ValueError, match="significance_level"):
        service.run(
            method=StatisticalTestMethod.MANN_KENDALL,
            series=(series,),
            significance_level=1.0,
        )
