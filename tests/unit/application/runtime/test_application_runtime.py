from unittest.mock import Mock

import pytest

from earth_twin_engine.application.core import (
    ApplicationConfiguration,
    ApplicationContext,
    ModuleManager,
    ServiceRegistry,
)
from earth_twin_engine.application.resource_management import ResourceManager
from earth_twin_engine.application.runtime import (
    ApplicationRuntime,
    RuntimeState,
)


@pytest.fixture
def dependencies() -> tuple[ModuleManager, ApplicationContext, ResourceManager]:
    manager = ModuleManager()
    context = ApplicationContext(
        configuration=ApplicationConfiguration(
            application_name="Earth Twin Engine",
        ),
        services=ServiceRegistry(),
    )
    resources = ResourceManager()

    return manager, context, resources


@pytest.fixture
def runtime(
    dependencies: tuple[ModuleManager, ApplicationContext, ResourceManager],
) -> ApplicationRuntime:
    manager, context, resources = dependencies
    return ApplicationRuntime(manager, context, resources)


def test_initial_state(runtime: ApplicationRuntime) -> None:
    assert runtime.state is RuntimeState.CREATED


def test_context_is_exposed(
    dependencies: tuple[ModuleManager, ApplicationContext, ResourceManager],
    runtime: ApplicationRuntime,
) -> None:
    assert runtime.context is dependencies[1]


def test_initialize(runtime: ApplicationRuntime) -> None:
    runtime.initialize()

    assert runtime.state is RuntimeState.INITIALIZED


def test_cannot_start_before_initialization(runtime: ApplicationRuntime) -> None:
    with pytest.raises(RuntimeError):
        runtime.start()


def test_start(runtime: ApplicationRuntime) -> None:
    runtime.initialize()
    runtime.start()

    assert runtime.state is RuntimeState.RUNNING


def test_update(runtime: ApplicationRuntime) -> None:
    runtime.initialize()
    runtime.start()

    runtime.update(0.016)

    assert runtime.state is RuntimeState.RUNNING


@pytest.mark.parametrize("delta_time", [-1.0, float("inf"), float("-inf"), float("nan")])
def test_reject_invalid_delta_time(
    runtime: ApplicationRuntime,
    delta_time: float,
) -> None:
    runtime.initialize()
    runtime.start()

    with pytest.raises(ValueError):
        runtime.update(delta_time)


@pytest.mark.parametrize("delta_time", [True, "0.016", None])
def test_reject_invalid_delta_time_type(
    runtime: ApplicationRuntime,
    delta_time: object,
) -> None:
    runtime.initialize()
    runtime.start()

    with pytest.raises(TypeError):
        runtime.update(delta_time)  # type: ignore[arg-type]


def test_stop(runtime: ApplicationRuntime) -> None:
    runtime.initialize()
    runtime.start()
    runtime.stop()

    assert runtime.state is RuntimeState.STOPPED


def test_cannot_update_after_stop(runtime: ApplicationRuntime) -> None:
    runtime.initialize()
    runtime.start()
    runtime.stop()

    with pytest.raises(RuntimeError):
        runtime.update(0.016)


def test_shutdown_from_created_state(runtime: ApplicationRuntime) -> None:
    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN


def test_shutdown_from_initialized_state(runtime: ApplicationRuntime) -> None:
    runtime.initialize()
    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN


def test_shutdown_from_running_state(runtime: ApplicationRuntime) -> None:
    runtime.initialize()
    runtime.start()
    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN


def test_shutdown_is_idempotent(runtime: ApplicationRuntime) -> None:
    runtime.initialize()
    runtime.start()

    runtime.shutdown()
    runtime.shutdown()

    assert runtime.state is RuntimeState.SHUTDOWN


def test_shutdown_releases_resources(
    dependencies: tuple[ModuleManager, ApplicationContext, ResourceManager],
) -> None:
    manager, context, resources = dependencies
    cleanup = Mock()
    resources.register("test_resource", object(), cleanup)

    runtime = ApplicationRuntime(manager, context, resources)
    runtime.shutdown()

    cleanup.assert_called_once()
    assert resources.is_shutdown is True


def test_shutdown_preserves_cleanup_failures(
    dependencies: tuple[ModuleManager, ApplicationContext, ResourceManager],
) -> None:
    manager, context, resources = dependencies

    def fail_cleanup(_: object) -> None:
        raise RuntimeError("Cleanup failed")

    resources.register("test_resource", object(), fail_cleanup)

    runtime = ApplicationRuntime(manager, context, resources)
    runtime.shutdown()

    assert len(runtime.cleanup_failures) == 1
    assert runtime.cleanup_failures[0].resource_id == "test_resource"


def test_initialization_failure_sets_failed_state(
    runtime: ApplicationRuntime,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_initialization(_: ApplicationContext) -> None:
        raise RuntimeError("Initialization failed")

    monkeypatch.setattr(
        runtime._module_manager,
        "initialize_all",
        fail_initialization,
    )

    with pytest.raises(RuntimeError, match="Initialization failed"):
        runtime.initialize()

    assert runtime.state is RuntimeState.FAILED
