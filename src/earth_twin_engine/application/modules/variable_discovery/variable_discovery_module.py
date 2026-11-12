"""Application module providing Earth science variable discovery."""

from math import isfinite

from earth_twin_engine.application.core.application_context import (
    ApplicationContext,
)
from earth_twin_engine.application.core.application_module import ApplicationModule
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.core.service_registry import ServiceRegistry
from earth_twin_engine.application.modules.variable_discovery.queries import (
    DiscoverEarthVariablesQuery,
    GetEarthVariableQuery,
)
from earth_twin_engine.application.modules.variable_discovery.query_handlers import (
    DiscoverEarthVariablesHandler,
    GetEarthVariableHandler,
)
from earth_twin_engine.application.modules.variable_discovery.variable_catalog import (
    VariableCatalog,
)
from earth_twin_engine.application.queries.query_dispatcher import QueryDispatcher


class VariableDiscoveryModule(ApplicationModule):
    """Owns the variable catalog and exposes its discovery queries."""

    def __init__(self, catalog: VariableCatalog | None = None) -> None:
        if catalog is not None and not isinstance(catalog, VariableCatalog):
            raise TypeError("catalog must be a VariableCatalog or None")

        self._metadata = ModuleMetadata(
            module_id="variable_discovery",
            name="Variable Discovery",
            version="1.0.0",
        )
        self._catalog = catalog if catalog is not None else VariableCatalog()
        self._services: ServiceRegistry | None = None
        self._dispatcher: QueryDispatcher | None = None
        self._initialized = False
        self._running = False

    @property
    def metadata(self) -> ModuleMetadata:
        return self._metadata

    @property
    def catalog(self) -> VariableCatalog:
        """Return the catalog owned by this module."""

        return self._catalog

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def is_running(self) -> bool:
        return self._running

    def initialize(self, context: ApplicationContext) -> None:
        if not isinstance(context, ApplicationContext):
            raise TypeError("context must be an ApplicationContext")

        if self._initialized:
            raise RuntimeError("variable discovery module is already initialized")

        services = context.services
        dispatcher = context.get_service(QueryDispatcher)

        if not isinstance(dispatcher, QueryDispatcher):
            raise RuntimeError("QueryDispatcher is not registered in the application context")

        if services.is_registered(VariableCatalog):
            raise RuntimeError("VariableCatalog is already registered")

        services.register(VariableCatalog, self._catalog)

        registered_queries: list[type] = []

        try:
            dispatcher.register(
                GetEarthVariableQuery,
                GetEarthVariableHandler(self._catalog),
            )
            registered_queries.append(GetEarthVariableQuery)

            dispatcher.register(
                DiscoverEarthVariablesQuery,
                DiscoverEarthVariablesHandler(self._catalog),
            )
            registered_queries.append(DiscoverEarthVariablesQuery)
        except Exception:
            for query_type in reversed(registered_queries):
                dispatcher.unregister(query_type)

            services.unregister(VariableCatalog)
            raise

        self._services = services
        self._dispatcher = dispatcher
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            raise RuntimeError("module must be initialized before starting")

        if self._running:
            raise RuntimeError("module is already running")

        self._running = True

    def update(self, delta_time: float) -> None:
        if isinstance(delta_time, bool) or not isinstance(delta_time, (int, float)):
            raise TypeError("delta_time must be numeric")

        if not isfinite(delta_time) or delta_time < 0:
            raise ValueError("delta_time must be finite and non-negative")

        if not self._running:
            raise RuntimeError("module must be running before updating")

    def stop(self) -> None:
        if not self._initialized:
            raise RuntimeError("module has not been initialized")

        self._running = False

    def shutdown(self) -> None:
        if not self._initialized:
            raise RuntimeError("module has not been initialized")

        if self._running:
            self.stop()

        if self._dispatcher is not None:
            self._dispatcher.unregister(GetEarthVariableQuery)
            self._dispatcher.unregister(DiscoverEarthVariablesQuery)

        if self._services is not None:
            self._services.unregister(VariableCatalog)

        self._dispatcher = None
        self._services = None
        self._initialized = False
