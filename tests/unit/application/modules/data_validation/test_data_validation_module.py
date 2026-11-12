"""Tests for the Data Validation application module."""

import pytest

from earth_twin_engine.application.launcher.application_launcher import (
    ApplicationLauncher,
)
from earth_twin_engine.application.modules.data_validation import (
    DataValidationModule,
)
from earth_twin_engine.application.modules.data_validation.commands import (
    ValidateDatasetCommand,
)
from earth_twin_engine.application.modules.data_validation.events import (
    DatasetValidatedEvent,
)


@pytest.fixture
def launcher() -> ApplicationLauncher:
    return ApplicationLauncher.from_configuration_file()


def test_module_metadata() -> None:
    module = DataValidationModule()

    assert module.metadata.module_id == "data_validation"
    assert module.metadata.name == "Data Validation"
    assert module.metadata.version == "1.0.0"
    assert module.metadata.dependencies == ()


def test_module_initialization_registers_command_handler(launcher) -> None:
    module = DataValidationModule()

    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.command_dispatcher.is_registered(ValidateDatasetCommand)


def test_module_can_start_update_and_stop(launcher) -> None:
    module = DataValidationModule()
    module.initialize(launcher.context)

    module.start()

    assert module.is_running

    module.update(0.016)
    module.update(1)

    module.stop()

    assert not module.is_running


def test_module_shutdown_unregisters_command_handler(launcher) -> None:
    module = DataValidationModule()
    module.initialize(launcher.context)

    module.start()
    module.shutdown()

    assert not module.is_initialized
    assert not module.is_running
    assert not launcher.command_dispatcher.is_registered(ValidateDatasetCommand)


def test_module_initialization_is_idempotency_protected(launcher) -> None:
    module = DataValidationModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="already initialized"):
        module.initialize(launcher.context)


def test_module_requires_initialization_before_start() -> None:
    module = DataValidationModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.start()


def test_module_requires_initialization_before_stop() -> None:
    module = DataValidationModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.stop()


def test_module_requires_start_before_update(launcher) -> None:
    module = DataValidationModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="running"):
        module.update(0.1)


def test_module_rejects_invalid_delta_time(launcher) -> None:
    module = DataValidationModule()
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
    module = DataValidationModule()

    module.shutdown()

    assert not module.is_initialized
    assert not module.is_running


def test_module_rejects_missing_required_services(launcher) -> None:
    module = DataValidationModule()

    launcher.context.services.unregister(type(launcher.command_dispatcher))

    with pytest.raises((RuntimeError, KeyError)):
        module.initialize(launcher.context)

    assert not module.is_initialized
    assert not launcher.command_dispatcher.is_registered(ValidateDatasetCommand)


def test_module_rejects_existing_command_handler(launcher) -> None:
    class ExistingHandler:
        def handle(self, command: ValidateDatasetCommand):
            return "existing handler"

    existing_handler = ExistingHandler()

    launcher.command_dispatcher.register(
        ValidateDatasetCommand,
        existing_handler,
    )

    module = DataValidationModule()

    with pytest.raises(RuntimeError, match="already registered"):
        module.initialize(launcher.context)

    assert not module.is_initialized
    assert launcher.command_dispatcher.is_registered(ValidateDatasetCommand)

    result = launcher.command_dispatcher.dispatch(
        ValidateDatasetCommand(
            dataset=make_dataset_for_dispatch(),
            time_series=(),
        )
    )

    assert result.failure is None
    assert result.value == "existing handler"


def make_dataset_for_dispatch():
    """Create a minimal valid dataset for command-dispatch testing."""

    from datetime import UTC, datetime

    from earth_twin_engine.domain.datasets import (
        DataProvenance,
        DataRequest,
        Dataset,
        DatasetMetadata,
        DataSource,
    )
    from earth_twin_engine.domain.geography import (
        GeographicRegion,
        SpatialBoundary,
    )
    from earth_twin_engine.domain.temporal import TemporalRange, TemporalResolution
    from earth_twin_engine.domain.variables import (
        EarthVariable,
        VariableCategory,
        VariableMetadata,
    )

    variable = EarthVariable(
        variable_id="air_temperature",
        name="Air Temperature",
        description="Air temperature.",
        category=VariableCategory.ATMOSPHERE,
        metadata=VariableMetadata(
            unit="K",
            temporal_resolutions=(TemporalResolution.DAILY,),
        ),
    )

    region = GeographicRegion(
        region_id="india",
        name="India",
        boundary=SpatialBoundary(
            south_latitude=6,
            north_latitude=37,
            west_longitude=68,
            east_longitude=98,
        ),
    )

    temporal_range = TemporalRange(
        start=datetime(2020, 1, 1, tzinfo=UTC),
        end=datetime(2021, 1, 1, tzinfo=UTC),
    )

    request = DataRequest(
        variable=variable,
        region=region,
        temporal_range=temporal_range,
        temporal_resolution=TemporalResolution.DAILY,
    )

    source = DataSource(
        source_id="nasa_merra2",
        name="MERRA-2",
        provider="NASA",
    )

    return Dataset(
        dataset_id="india_daily_temperature",
        request=request,
        metadata=DatasetMetadata(title="India Daily Temperature"),
        provenance=DataProvenance(
            source=source,
            retrieved_at=datetime(2026, 1, 1, tzinfo=UTC),
        ),
    )


def test_module_can_be_initialized_again_after_shutdown(launcher) -> None:
    module = DataValidationModule()

    module.initialize(launcher.context)
    module.shutdown()
    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.command_dispatcher.is_registered(ValidateDatasetCommand)


def test_command_dispatch_validates_dataset_and_publishes_event(
    launcher,
    dataset,
    valid_time_series_collection,
) -> None:
    module = DataValidationModule()
    module.initialize(launcher.context)
    module.start()

    events = []
    launcher.event_dispatcher.subscribe(DatasetValidatedEvent, events.append)

    command = ValidateDatasetCommand(
        dataset=dataset,
        time_series=valid_time_series_collection,
    )

    result = launcher.command_dispatcher.dispatch(command)

    assert result.failure is None
    assert result.value.is_valid
    assert result.value.dataset_id == dataset.dataset_id

    assert len(events) == 1
    assert events[0].dataset_id == dataset.dataset_id
    assert events[0].command_id == command.command_id
    assert events[0].validation_result is result.value


def test_module_rolls_back_failed_command_registration(
    launcher,
    monkeypatch,
) -> None:
    original_register = launcher.command_dispatcher.register

    def register_then_fail(command_type, handler) -> None:
        original_register(command_type, handler)
        raise RuntimeError("Simulated registration failure")

    monkeypatch.setattr(
        launcher.command_dispatcher,
        "register",
        register_then_fail,
    )

    module = DataValidationModule()

    with pytest.raises(RuntimeError, match="Simulated registration failure"):
        module.initialize(launcher.context)

    assert not module.is_initialized
    assert not launcher.command_dispatcher.is_registered(ValidateDatasetCommand)
