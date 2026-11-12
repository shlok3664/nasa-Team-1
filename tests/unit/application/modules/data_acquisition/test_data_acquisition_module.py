"""Tests for the Data Acquisition application module."""

from datetime import UTC, datetime

import pytest

from earth_twin_engine.application.launcher.application_launcher import (
    ApplicationLauncher,
)
from earth_twin_engine.application.modules.data_acquisition import (
    DataAcquisitionModule,
)
from earth_twin_engine.application.modules.data_acquisition.commands import (
    AcquireDatasetCommand,
)
from earth_twin_engine.application.modules.data_acquisition.events import (
    DatasetAcquiredEvent,
)
from earth_twin_engine.application.modules.data_source_manager import (
    DataSourceManager,
)
from earth_twin_engine.application.modules.region_manager import RegionManager
from earth_twin_engine.application.modules.variable_discovery import VariableCatalog
from earth_twin_engine.domain.temporal import TemporalRange, TemporalResolution


@pytest.fixture
def launcher() -> ApplicationLauncher:
    return ApplicationLauncher.from_configuration_file()


def register_acquisition_services(
    launcher: ApplicationLauncher,
    variable_catalog: VariableCatalog,
    region_manager: RegionManager,
    data_source_manager: DataSourceManager,
) -> None:
    launcher.context.services.register(VariableCatalog, variable_catalog)
    launcher.context.services.register(RegionManager, region_manager)
    launcher.context.services.register(DataSourceManager, data_source_manager)


def make_temporal_range() -> TemporalRange:
    return TemporalRange(
        start=datetime(2020, 1, 1, tzinfo=UTC),
        end=datetime(2021, 1, 1, tzinfo=UTC),
    )


def test_module_metadata() -> None:
    module = DataAcquisitionModule()

    assert module.metadata.module_id == "data_acquisition"
    assert module.metadata.name == "Data Acquisition"
    assert module.metadata.version == "1.0.0"
    assert module.metadata.dependencies == (
        "variable_discovery",
        "region_manager",
        "data_source_manager",
    )


def test_module_initialization_registers_command_handler(
    launcher,
    variable_catalog,
    region_manager,
    data_source_manager,
) -> None:
    register_acquisition_services(
        launcher,
        variable_catalog,
        region_manager,
        data_source_manager,
    )
    module = DataAcquisitionModule()

    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.command_dispatcher.is_registered(AcquireDatasetCommand)


def test_module_can_start_update_and_stop(
    launcher,
    variable_catalog,
    region_manager,
    data_source_manager,
) -> None:
    register_acquisition_services(
        launcher,
        variable_catalog,
        region_manager,
        data_source_manager,
    )
    module = DataAcquisitionModule()
    module.initialize(launcher.context)

    module.start()

    assert module.is_running

    module.update(0.016)
    module.update(1)

    module.stop()

    assert not module.is_running


def test_module_shutdown_unregisters_command_handler(
    launcher,
    variable_catalog,
    region_manager,
    data_source_manager,
) -> None:
    register_acquisition_services(
        launcher,
        variable_catalog,
        region_manager,
        data_source_manager,
    )
    module = DataAcquisitionModule()
    module.initialize(launcher.context)

    module.start()
    module.shutdown()

    assert not module.is_initialized
    assert not module.is_running
    assert not launcher.command_dispatcher.is_registered(AcquireDatasetCommand)


def test_module_initialization_is_idempotency_protected(
    launcher,
    variable_catalog,
    region_manager,
    data_source_manager,
) -> None:
    register_acquisition_services(
        launcher,
        variable_catalog,
        region_manager,
        data_source_manager,
    )
    module = DataAcquisitionModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="already initialized"):
        module.initialize(launcher.context)


def test_module_requires_initialization_before_start() -> None:
    module = DataAcquisitionModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.start()


def test_module_requires_initialization_before_stop() -> None:
    module = DataAcquisitionModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.stop()


def test_module_requires_start_before_update(
    launcher,
    variable_catalog,
    region_manager,
    data_source_manager,
) -> None:
    register_acquisition_services(
        launcher,
        variable_catalog,
        region_manager,
        data_source_manager,
    )
    module = DataAcquisitionModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="running"):
        module.update(0.1)


def test_module_rejects_invalid_delta_time(
    launcher,
    variable_catalog,
    region_manager,
    data_source_manager,
) -> None:
    register_acquisition_services(
        launcher,
        variable_catalog,
        region_manager,
        data_source_manager,
    )
    module = DataAcquisitionModule()
    module.initialize(launcher.context)
    module.start()

    with pytest.raises(TypeError):
        module.update("invalid")  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        module.update(True)

    with pytest.raises(ValueError):
        module.update(-1)

    with pytest.raises(ValueError):
        module.update(float("inf"))

    with pytest.raises(ValueError):
        module.update(float("nan"))


def test_module_shutdown_before_initialization_is_safe() -> None:
    module = DataAcquisitionModule()

    module.shutdown()

    assert not module.is_initialized
    assert not module.is_running


def test_module_rejects_missing_required_services(launcher) -> None:
    module = DataAcquisitionModule()

    with pytest.raises((RuntimeError, KeyError)):
        module.initialize(launcher.context)

    assert not module.is_initialized
    assert not launcher.command_dispatcher.is_registered(AcquireDatasetCommand)


def test_module_rejects_existing_command_handler(
    launcher,
    variable_catalog,
    region_manager,
    data_source_manager,
) -> None:
    register_acquisition_services(
        launcher,
        variable_catalog,
        region_manager,
        data_source_manager,
    )

    class ExistingHandler:
        def handle(self, command: AcquireDatasetCommand):
            return "existing handler"

    existing_handler = ExistingHandler()
    launcher.command_dispatcher.register(
        AcquireDatasetCommand,
        existing_handler,
    )

    module = DataAcquisitionModule()

    with pytest.raises(RuntimeError, match="already registered"):
        module.initialize(launcher.context)

    assert not module.is_initialized
    assert launcher.command_dispatcher.is_registered(AcquireDatasetCommand)

    result = launcher.command_dispatcher.dispatch(
        AcquireDatasetCommand(
            variable_id="air_temperature",
            region_id="india",
            temporal_range=make_temporal_range(),
            temporal_resolution=TemporalResolution.DAILY,
        )
    )

    assert result.failure is None
    assert result.value == "existing handler"


def test_module_can_be_initialized_again_after_shutdown(
    launcher,
    variable_catalog,
    region_manager,
    data_source_manager,
) -> None:
    register_acquisition_services(
        launcher,
        variable_catalog,
        region_manager,
        data_source_manager,
    )
    module = DataAcquisitionModule()

    module.initialize(launcher.context)
    module.shutdown()
    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.command_dispatcher.is_registered(AcquireDatasetCommand)


def test_command_dispatch_acquires_dataset_and_publishes_event(
    launcher,
    variable_catalog,
    region_manager,
    data_source_manager,
    temporal_range,
    dataset,
) -> None:
    register_acquisition_services(
        launcher,
        variable_catalog,
        region_manager,
        data_source_manager,
    )
    module = DataAcquisitionModule()
    module.initialize(launcher.context)
    module.start()

    events = []
    launcher.event_dispatcher.subscribe(DatasetAcquiredEvent, events.append)

    command = AcquireDatasetCommand(
        variable_id="air_temperature",
        region_id="india",
        temporal_range=temporal_range,
        temporal_resolution=TemporalResolution.DAILY,
    )

    result = launcher.command_dispatcher.dispatch(command)

    assert result.failure is None
    assert result.value is dataset
    assert len(events) == 1
    assert events[0].dataset is dataset
    assert events[0].command_id == command.command_id
