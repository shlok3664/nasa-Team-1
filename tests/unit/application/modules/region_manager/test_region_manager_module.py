import pytest

from earth_twin_engine.application.core.application_configuration import (
    ApplicationConfiguration,
)
from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.service_registry import ServiceRegistry
from earth_twin_engine.application.launcher.application_launcher import (
    ApplicationLauncher,
)
from earth_twin_engine.application.modules.region_manager import (
    FindRegionsContainingQuery,
    GetGeographicRegionQuery,
    ListGeographicRegionsQuery,
    RegionManager,
    RegionManagerModule,
)
from earth_twin_engine.application.queries import QueryDispatcher


@pytest.fixture
def launcher() -> ApplicationLauncher:
    return ApplicationLauncher.from_configuration_file()


def test_module_metadata() -> None:
    module = RegionManagerModule()

    assert module.metadata.module_id == "region_manager"
    assert module.metadata.name == "Region Manager"
    assert module.metadata.version == "1.0.0"
    assert module.metadata.dependencies == ()


def test_module_initialization_registers_service_and_queries(
    launcher: ApplicationLauncher,
) -> None:
    module = RegionManagerModule()

    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.context.resolve(RegionManager) is module.manager

    assert launcher.query_dispatcher.is_registered(GetGeographicRegionQuery)
    assert launcher.query_dispatcher.is_registered(ListGeographicRegionsQuery)
    assert launcher.query_dispatcher.is_registered(FindRegionsContainingQuery)


def test_module_can_start_update_and_stop(
    launcher: ApplicationLauncher,
) -> None:
    module = RegionManagerModule()
    module.initialize(launcher.context)

    module.start()

    assert module.is_running

    module.update(0.016)
    module.update(1)

    module.stop()

    assert not module.is_running


def test_module_shutdown_unregisters_service_and_queries(
    launcher: ApplicationLauncher,
) -> None:
    module = RegionManagerModule()
    module.initialize(launcher.context)

    module.start()
    module.shutdown()

    assert not module.is_initialized
    assert not module.is_running
    assert not launcher.context.services.is_registered(RegionManager)

    assert not launcher.query_dispatcher.is_registered(GetGeographicRegionQuery)
    assert not launcher.query_dispatcher.is_registered(ListGeographicRegionsQuery)
    assert not launcher.query_dispatcher.is_registered(FindRegionsContainingQuery)


def test_module_initialization_is_idempotency_protected(
    launcher: ApplicationLauncher,
) -> None:
    module = RegionManagerModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="already initialized"):
        module.initialize(launcher.context)


def test_module_requires_initialization_before_start() -> None:
    module = RegionManagerModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.start()


def test_module_requires_initialization_before_stop() -> None:
    module = RegionManagerModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.stop()


def test_module_requires_start_before_update(
    launcher: ApplicationLauncher,
) -> None:
    module = RegionManagerModule()
    module.initialize(launcher.context)

    with pytest.raises(RuntimeError, match="running"):
        module.update(0.1)


def test_module_rejects_invalid_delta_time(
    launcher: ApplicationLauncher,
) -> None:
    module = RegionManagerModule()
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
    module = RegionManagerModule()

    module.shutdown()

    assert not module.is_initialized
    assert not module.is_running


def test_module_rejects_invalid_manager() -> None:
    with pytest.raises(TypeError, match="RegionManager"):
        RegionManagerModule(object())  # type: ignore[arg-type]


def test_module_rejects_missing_query_dispatcher() -> None:
    context = ApplicationContext(
        configuration=ApplicationConfiguration(
            application_name="Test Application",
        ),
        services=ServiceRegistry(),
    )

    module = RegionManagerModule()

    with pytest.raises(RuntimeError, match="QueryDispatcher"):
        module.initialize(context)

    assert not module.is_initialized


def test_module_rejects_existing_region_manager_service(
    launcher: ApplicationLauncher,
) -> None:
    existing_manager = RegionManager()
    launcher.context.services.register(RegionManager, existing_manager)

    module = RegionManagerModule()

    with pytest.raises(RuntimeError, match="RegionManager service"):
        module.initialize(launcher.context)

    assert not module.is_initialized
    assert launcher.context.resolve(RegionManager) is existing_manager

    assert not launcher.query_dispatcher.is_registered(GetGeographicRegionQuery)
    assert not launcher.query_dispatcher.is_registered(ListGeographicRegionsQuery)
    assert not launcher.query_dispatcher.is_registered(FindRegionsContainingQuery)


def test_module_rolls_back_partial_query_registration(
    launcher: ApplicationLauncher,
) -> None:
    dispatcher: QueryDispatcher = launcher.query_dispatcher

    class ExistingHandler:
        def handle(self, query: ListGeographicRegionsQuery) -> tuple:
            return ()

    existing_handler = ExistingHandler()

    dispatcher.register(
        ListGeographicRegionsQuery,
        existing_handler,
    )

    module = RegionManagerModule()

    with pytest.raises(RuntimeError, match="already registered"):
        module.initialize(launcher.context)

    # The service registered before the failure must be removed.
    assert not launcher.context.services.is_registered(RegionManager)

    # The first query registration must be rolled back.
    assert not dispatcher.is_registered(GetGeographicRegionQuery)

    # The pre-existing handler must remain untouched.
    assert dispatcher.is_registered(ListGeographicRegionsQuery)

    # The third query must never have been registered.
    assert not dispatcher.is_registered(FindRegionsContainingQuery)

    assert not module.is_initialized
    assert not module.is_running


def test_module_can_be_initialized_again_after_shutdown(
    launcher: ApplicationLauncher,
) -> None:
    module = RegionManagerModule()

    module.initialize(launcher.context)
    module.shutdown()

    module.initialize(launcher.context)

    assert module.is_initialized
    assert launcher.context.resolve(RegionManager) is module.manager

    assert launcher.query_dispatcher.is_registered(GetGeographicRegionQuery)
    assert launcher.query_dispatcher.is_registered(ListGeographicRegionsQuery)
    assert launcher.query_dispatcher.is_registered(FindRegionsContainingQuery)
