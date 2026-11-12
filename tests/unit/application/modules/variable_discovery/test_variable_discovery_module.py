import pytest

from earth_twin_engine.application.launcher.application_launcher import (
    ApplicationLauncher,
)
from earth_twin_engine.application.modules.variable_discovery import (
    DiscoverEarthVariablesQuery,
    GetEarthVariableQuery,
    VariableCatalog,
    VariableDiscoveryModule,
)
from earth_twin_engine.application.queries.query_dispatcher import QueryDispatcher


@pytest.fixture
def launcher() -> ApplicationLauncher:
    return ApplicationLauncher.from_configuration_file()


def test_module_metadata() -> None:
    module = VariableDiscoveryModule()

    assert module.metadata.module_id == "variable_discovery"
    assert module.metadata.name == "Variable Discovery"
    assert module.metadata.version == "1.0.0"
    assert module.metadata.dependencies == ()


def test_module_initialization_registers_services_and_queries(
    launcher: ApplicationLauncher,
) -> None:
    module = VariableDiscoveryModule()

    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.context.resolve(VariableCatalog) is module.catalog
    assert launcher.query_dispatcher.is_registered(GetEarthVariableQuery)
    assert launcher.query_dispatcher.is_registered(DiscoverEarthVariablesQuery)


def test_module_can_start_update_and_stop(
    launcher: ApplicationLauncher,
) -> None:
    module = VariableDiscoveryModule()
    module.initialize(launcher.context)

    module.start()

    assert module.is_running

    module.update(0.016)
    module.update(1)

    module.stop()

    assert not module.is_running


def test_module_shutdown_unregisters_services_and_queries(
    launcher: ApplicationLauncher,
) -> None:
    module = VariableDiscoveryModule()
    module.initialize(launcher.context)

    module.start()
    module.shutdown()

    assert not module.is_initialized
    assert not module.is_running
    assert not launcher.context.services.is_registered(VariableCatalog)
    assert not launcher.query_dispatcher.is_registered(GetEarthVariableQuery)
    assert not launcher.query_dispatcher.is_registered(DiscoverEarthVariablesQuery)


def test_module_initialization_is_idempotency_protected(
    launcher: ApplicationLauncher,
) -> None:
    module = VariableDiscoveryModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="already initialized"):
        module.initialize(launcher.context)


def test_module_requires_initialization_before_start() -> None:
    module = VariableDiscoveryModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.start()


def test_module_requires_start_before_update(
    launcher: ApplicationLauncher,
) -> None:
    module = VariableDiscoveryModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="running"):
        module.update(0.1)


def test_module_rejects_invalid_delta_time(
    launcher: ApplicationLauncher,
) -> None:
    module = VariableDiscoveryModule()
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


def test_module_rejects_shutdown_before_initialization() -> None:
    module = VariableDiscoveryModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.shutdown()


def test_module_rejects_invalid_catalog() -> None:
    with pytest.raises(TypeError):
        VariableDiscoveryModule(object())  # type: ignore[arg-type]


def test_module_rejects_missing_query_dispatcher() -> None:
    from earth_twin_engine.application.core.application_configuration import (
        ApplicationConfiguration,
    )
    from earth_twin_engine.application.core.application_context import (
        ApplicationContext,
    )
    from earth_twin_engine.application.core.service_registry import ServiceRegistry

    context = ApplicationContext(
        configuration=ApplicationConfiguration(
            application_name="Test Application",
        ),
        services=ServiceRegistry(),
    )

    module = VariableDiscoveryModule()

    with pytest.raises(RuntimeError, match="QueryDispatcher"):
        module.initialize(context)


def test_module_rolls_back_partial_query_registration(
    launcher: ApplicationLauncher,
) -> None:
    dispatcher: QueryDispatcher = launcher.query_dispatcher

    class ExistingHandler:
        def handle(self, query: DiscoverEarthVariablesQuery) -> tuple:
            return ()

    dispatcher.register(
        DiscoverEarthVariablesQuery,
        ExistingHandler(),
    )

    module = VariableDiscoveryModule()

    with pytest.raises(ValueError, match="already registered"):
        module.initialize(launcher.context)

    assert not launcher.context.services.is_registered(VariableCatalog)
    assert not dispatcher.is_registered(GetEarthVariableQuery)
    assert dispatcher.is_registered(DiscoverEarthVariablesQuery)


def test_module_can_be_initialized_again_after_shutdown(
    launcher: ApplicationLauncher,
) -> None:
    module = VariableDiscoveryModule()

    module.initialize(launcher.context)
    module.shutdown()

    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.context.resolve(VariableCatalog) is module.catalog
