import pytest

from earth_twin_engine.application.commands import CommandDispatcher
from earth_twin_engine.application.core import (
    ApplicationConfiguration,
    ModuleManager,
)
from earth_twin_engine.application.error_handling import ApplicationErrorHandler
from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.launcher import ApplicationLauncher
from earth_twin_engine.application.logging import LoggerFactory
from earth_twin_engine.application.queries import QueryDispatcher
from earth_twin_engine.application.resource_management import ResourceManager
from earth_twin_engine.application.runtime import (
    ApplicationRuntime,
    RuntimeState,
)


@pytest.fixture
def launcher() -> ApplicationLauncher:
    configuration = ApplicationConfiguration(
        application_name="Earth Twin Engine",
        environment="testing",
        debug=True,
    )

    return ApplicationLauncher(configuration)


def test_create_launcher(launcher: ApplicationLauncher) -> None:
    assert isinstance(launcher.runtime, ApplicationRuntime)
    assert launcher.runtime.state is RuntimeState.CREATED


def test_context_contains_core_services(
    launcher: ApplicationLauncher,
) -> None:
    assert isinstance(launcher.context.resolve(ModuleManager), ModuleManager)
    assert isinstance(launcher.context.resolve(ResourceManager), ResourceManager)
    assert isinstance(launcher.context.resolve(EventDispatcher), EventDispatcher)
    assert isinstance(
        launcher.context.resolve(CommandDispatcher),
        CommandDispatcher,
    )
    assert isinstance(
        launcher.context.resolve(QueryDispatcher),
        QueryDispatcher,
    )
    assert isinstance(
        launcher.context.resolve(ApplicationErrorHandler),
        ApplicationErrorHandler,
    )
    assert isinstance(launcher.context.resolve(LoggerFactory), LoggerFactory)


def test_launcher_exposes_module_manager(
    launcher: ApplicationLauncher,
) -> None:
    assert launcher.context.resolve(ModuleManager) is launcher.module_manager


def test_launcher_exposes_shared_messaging_services(
    launcher: ApplicationLauncher,
) -> None:
    assert launcher.context.resolve(EventDispatcher) is launcher.event_dispatcher
    assert launcher.context.resolve(CommandDispatcher) is launcher.command_dispatcher
    assert launcher.context.resolve(QueryDispatcher) is launcher.query_dispatcher


def test_launch_initializes_and_starts_runtime(
    launcher: ApplicationLauncher,
) -> None:
    runtime = launcher.launch()

    assert runtime is launcher.runtime
    assert runtime.state is RuntimeState.RUNNING


def test_reject_invalid_configuration() -> None:
    with pytest.raises(TypeError):
        ApplicationLauncher("invalid")  # type: ignore[arg-type]


def test_reject_invalid_module_manager() -> None:
    configuration = ApplicationConfiguration(
        application_name="Earth Twin Engine",
    )

    with pytest.raises(TypeError):
        ApplicationLauncher(
            configuration,
            module_manager="invalid",  # type: ignore[arg-type]
        )


def test_launcher_uses_supplied_module_manager() -> None:
    configuration = ApplicationConfiguration(
        application_name="Earth Twin Engine",
    )
    manager = ModuleManager()

    launcher = ApplicationLauncher(configuration, manager)

    assert launcher.module_manager is manager
    assert launcher.context.resolve(ModuleManager) is manager


def test_create_launcher_from_configuration_file(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
        {
            "application_name": "ETE Integration Test",
            "environment": "testing",
            "debug": true
        }
        """,
        encoding="utf-8",
    )

    launcher = ApplicationLauncher.from_configuration_file(
        config_path=str(config_path),
        environ={},
    )

    assert launcher.context.configuration.application_name == "ETE Integration Test"
    assert launcher.context.configuration.environment == "testing"
    assert launcher.context.configuration.debug is True


def test_create_launcher_from_environment() -> None:
    launcher = ApplicationLauncher.from_configuration_file(
        environ={
            "ETE_APPLICATION_NAME": "Environment ETE",
            "ETE_ENVIRONMENT": "testing",
            "ETE_DEBUG": "true",
        },
    )

    assert launcher.context.configuration.application_name == "Environment ETE"
    assert launcher.context.configuration.environment == "testing"
    assert launcher.context.configuration.debug is True
