"""Tests for the regional comparison application module."""

import pytest

from earth_twin_engine.application.launcher.application_launcher import (
    ApplicationLauncher,
)
from earth_twin_engine.application.modules.region_manager import RegionManager
from earth_twin_engine.application.modules.regional_comparison import (
    CompareRegionsCommand,
    RegionalComparisonCompletedEvent,
    RegionalComparisonModule,
)
from earth_twin_engine.application.modules.time_series_management import TimeSeriesManager


@pytest.fixture
def launcher() -> ApplicationLauncher:
    return ApplicationLauncher.from_configuration_file()


def register_comparison_services(
    launcher: ApplicationLauncher,
    region_manager: RegionManager,
    time_series_manager: TimeSeriesManager,
) -> None:
    launcher.context.services.register(RegionManager, region_manager)
    launcher.context.services.register(TimeSeriesManager, time_series_manager)


def test_module_metadata() -> None:
    module = RegionalComparisonModule()

    assert module.metadata.module_id == "regional_comparison"
    assert module.metadata.name == "Regional Comparison"
    assert module.metadata.version == "1.0.0"
    assert module.metadata.dependencies == (
        "region_manager",
        "time_series_management",
        "trend_analysis",
    )


def test_module_starts_uninitialized() -> None:
    module = RegionalComparisonModule()

    assert not module.is_initialized
    assert not module.is_running


def test_module_rejects_start_before_initialization() -> None:
    module = RegionalComparisonModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.start()


def test_module_rejects_update_before_initialization() -> None:
    module = RegionalComparisonModule()

    with pytest.raises(RuntimeError, match="running"):
        module.update(0.1)


def test_module_initialization_registers_command_handler(
    launcher,
    region_manager,
    populated_time_series_manager,
) -> None:
    register_comparison_services(
        launcher,
        region_manager,
        populated_time_series_manager,
    )
    module = RegionalComparisonModule()

    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.command_dispatcher.is_registered(CompareRegionsCommand)
    assert module.service is not None


def test_module_can_start_update_and_stop(
    launcher,
    region_manager,
    populated_time_series_manager,
) -> None:
    register_comparison_services(
        launcher,
        region_manager,
        populated_time_series_manager,
    )
    module = RegionalComparisonModule()
    module.initialize(launcher.context)

    module.start()

    assert module.is_running

    module.update(0.016)
    module.update(1.0)

    module.stop()

    assert not module.is_running


def test_module_shutdown_unregisters_command_handler(
    launcher,
    region_manager,
    populated_time_series_manager,
) -> None:
    register_comparison_services(
        launcher,
        region_manager,
        populated_time_series_manager,
    )
    module = RegionalComparisonModule()
    module.initialize(launcher.context)
    module.start()

    module.shutdown()

    assert not module.is_initialized
    assert not module.is_running
    assert not launcher.command_dispatcher.is_registered(CompareRegionsCommand)


def test_module_initialization_is_idempotency_protected(
    launcher,
    region_manager,
    populated_time_series_manager,
) -> None:
    register_comparison_services(
        launcher,
        region_manager,
        populated_time_series_manager,
    )
    module = RegionalComparisonModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="already initialized"):
        module.initialize(launcher.context)


def test_module_requires_initialization_before_stop() -> None:
    module = RegionalComparisonModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.stop()


def test_module_rejects_update_when_not_running(
    launcher,
    region_manager,
    populated_time_series_manager,
) -> None:
    register_comparison_services(
        launcher,
        region_manager,
        populated_time_series_manager,
    )
    module = RegionalComparisonModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="running"):
        module.update(0.1)


def test_module_rejects_invalid_delta_time(
    launcher,
    region_manager,
    populated_time_series_manager,
) -> None:
    register_comparison_services(
        launcher,
        region_manager,
        populated_time_series_manager,
    )
    module = RegionalComparisonModule()
    module.initialize(launcher.context)
    module.start()

    with pytest.raises(ValueError, match="delta_time must be finite and non-negative"):
        module.update("invalid")  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        module.update(True)

    with pytest.raises(ValueError):
        module.update(-1.0)

    with pytest.raises(ValueError):
        module.update(float("inf"))

    with pytest.raises(ValueError):
        module.update(float("nan"))


def test_module_shutdown_before_initialization_is_safe() -> None:
    module = RegionalComparisonModule()

    module.shutdown()

    assert not module.is_initialized
    assert not module.is_running


def test_module_rejects_missing_required_services(launcher) -> None:
    module = RegionalComparisonModule()

    with pytest.raises((RuntimeError, KeyError, TypeError)):
        module.initialize(launcher.context)

    assert not module.is_initialized
    assert not launcher.command_dispatcher.is_registered(CompareRegionsCommand)


def test_module_rejects_existing_command_handler(
    launcher,
    region_manager,
    populated_time_series_manager,
) -> None:
    register_comparison_services(
        launcher,
        region_manager,
        populated_time_series_manager,
    )

    class ExistingHandler:
        def handle(self, command: CompareRegionsCommand):
            return "existing handler"

    launcher.command_dispatcher.register(
        CompareRegionsCommand,
        ExistingHandler(),
    )

    module = RegionalComparisonModule()

    with pytest.raises(RuntimeError, match="already registered"):
        module.initialize(launcher.context)

    assert not module.is_initialized
    assert launcher.command_dispatcher.is_registered(CompareRegionsCommand)


def test_module_can_be_initialized_again_after_shutdown(
    launcher,
    region_manager,
    populated_time_series_manager,
) -> None:
    register_comparison_services(
        launcher,
        region_manager,
        populated_time_series_manager,
    )
    module = RegionalComparisonModule()

    module.initialize(launcher.context)
    module.shutdown()
    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.command_dispatcher.is_registered(CompareRegionsCommand)


@pytest.mark.parametrize(
    "significance_level",
    [0.0, 1.0, -0.1, 1.1, float("nan"), float("inf"), True],
)
def test_module_rejects_invalid_significance_level(
    significance_level: float,
) -> None:
    with pytest.raises(ValueError):
        RegionalComparisonModule(significance_level=significance_level)


def test_module_command_dispatch_publishes_completed_event(
    launcher,
    region_manager,
    populated_time_series_manager,
) -> None:
    register_comparison_services(
        launcher,
        region_manager,
        populated_time_series_manager,
    )
    module = RegionalComparisonModule()
    module.initialize(launcher.context)
    module.start()

    events = []
    launcher.event_dispatcher.subscribe(
        RegionalComparisonCompletedEvent,
        events.append,
    )

    command = CompareRegionsCommand(
        region_ids=("region_north", "region_south"),
        variable_id="surface_temperature",
    )

    dispatch_result = launcher.command_dispatcher.dispatch(command)

    assert dispatch_result.failure is None
    assert dispatch_result.value is not None
    assert dispatch_result.value.variable_id == "surface_temperature"
    assert len(events) == 1
    assert events[0].result is dispatch_result.value
    assert events[0].command_id == command.command_id
