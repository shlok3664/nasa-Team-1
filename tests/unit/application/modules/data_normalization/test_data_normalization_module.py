"""Tests for DataNormalizationModule."""

import pytest

from earth_twin_engine.application.launcher.application_launcher import (
    ApplicationLauncher,
)
from earth_twin_engine.application.modules.data_normalization import (
    DataNormalizationModule,
)
from earth_twin_engine.application.modules.data_normalization.commands import (
    NormalizeDatasetCommand,
)
from earth_twin_engine.application.modules.data_normalization.events import (
    DatasetNormalizedEvent,
)


@pytest.fixture
def launcher() -> ApplicationLauncher:
    return ApplicationLauncher.from_configuration_file()


def test_module_metadata() -> None:
    module = DataNormalizationModule()

    assert module.metadata.module_id == "data_normalization"
    assert module.metadata.name == "Data Normalization"
    assert module.metadata.version == "1.0.0"
    assert module.metadata.dependencies == ("data_validation",)


def test_module_initialization_registers_command_handler(launcher) -> None:
    module = DataNormalizationModule()

    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.command_dispatcher.is_registered(NormalizeDatasetCommand)


def test_module_can_start_update_and_stop(launcher) -> None:
    module = DataNormalizationModule()
    module.initialize(launcher.context)

    module.start()

    assert module.is_running

    module.update(0.016)
    module.update(1)

    module.stop()

    assert not module.is_running


def test_module_shutdown_unregisters_command_handler(launcher) -> None:
    module = DataNormalizationModule()
    module.initialize(launcher.context)

    module.start()
    module.shutdown()

    assert not module.is_initialized
    assert not module.is_running
    assert not launcher.command_dispatcher.is_registered(NormalizeDatasetCommand)


def test_module_prevents_double_initialization(launcher) -> None:
    module = DataNormalizationModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="already initialized"):
        module.initialize(launcher.context)


def test_module_requires_initialization_before_start() -> None:
    with pytest.raises(RuntimeError, match="initialized"):
        DataNormalizationModule().start()


def test_module_requires_initialization_before_stop() -> None:
    with pytest.raises(RuntimeError, match="initialized"):
        DataNormalizationModule().stop()


def test_module_requires_running_state_before_update(launcher) -> None:
    module = DataNormalizationModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="running"):
        module.update(0.1)


def test_module_rejects_invalid_delta_time(launcher) -> None:
    module = DataNormalizationModule()
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
    module = DataNormalizationModule()

    module.shutdown()

    assert not module.is_initialized
    assert not module.is_running


def test_module_rejects_missing_required_services(launcher) -> None:
    launcher.context.services.unregister(type(launcher.command_dispatcher))

    module = DataNormalizationModule()

    with pytest.raises((RuntimeError, KeyError)):
        module.initialize(launcher.context)

    assert not module.is_initialized
    assert not launcher.command_dispatcher.is_registered(NormalizeDatasetCommand)


def test_module_rejects_existing_command_handler(launcher) -> None:
    class ExistingHandler:
        def handle(self, command: NormalizeDatasetCommand):
            return "existing handler"

    existing_handler = ExistingHandler()

    launcher.command_dispatcher.register(
        NormalizeDatasetCommand,
        existing_handler,
    )

    module = DataNormalizationModule()

    with pytest.raises(RuntimeError, match="already registered"):
        module.initialize(launcher.context)

    assert not module.is_initialized
    assert launcher.command_dispatcher.is_registered(NormalizeDatasetCommand)


def test_module_can_reinitialize_after_shutdown(launcher) -> None:
    module = DataNormalizationModule()

    module.initialize(launcher.context)
    module.shutdown()
    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.command_dispatcher.is_registered(NormalizeDatasetCommand)


def test_module_rolls_back_failed_registration(launcher, monkeypatch) -> None:
    original_register = launcher.command_dispatcher.register

    def register_then_fail(command_type, handler) -> None:
        original_register(command_type, handler)
        raise RuntimeError("Simulated registration failure")

    monkeypatch.setattr(
        launcher.command_dispatcher,
        "register",
        register_then_fail,
    )

    module = DataNormalizationModule()

    with pytest.raises(RuntimeError, match="Simulated registration failure"):
        module.initialize(launcher.context)

    assert not module.is_initialized
    assert not launcher.command_dispatcher.is_registered(NormalizeDatasetCommand)


def test_command_dispatch_normalizes_and_publishes_event(
    launcher,
    dataset,
    celsius_series_collection,
) -> None:
    module = DataNormalizationModule()
    module.initialize(launcher.context)
    module.start()

    events = []
    launcher.event_dispatcher.subscribe(DatasetNormalizedEvent, events.append)

    command = NormalizeDatasetCommand(
        dataset=dataset,
        time_series=celsius_series_collection,
    )

    result = launcher.command_dispatcher.dispatch(command)

    assert result.failure is None
    assert result.value.dataset.dataset_id.endswith("_normalized")
    assert result.value.time_series[0].points[0].value == pytest.approx(285.4)

    assert len(events) == 1
    assert events[0].command_id == command.command_id
    assert events[0].normalization_result is result.value
