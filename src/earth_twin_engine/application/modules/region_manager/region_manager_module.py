"""Application module for geographic region management."""

from math import isfinite

from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.application_module import ApplicationModule
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.queries import QueryDispatcher

from .queries import (
    FindRegionsContainingQuery,
    GetGeographicRegionQuery,
    ListGeographicRegionsQuery,
)
from .query_handlers import (
    FindRegionsContainingHandler,
    GetGeographicRegionHandler,
    ListGeographicRegionsHandler,
)
from .region_manager import RegionManager


class RegionManagerModule(ApplicationModule):
    """Owns the geographic region manager and exposes its queries."""

    def __init__(self, manager: RegionManager | None = None) -> None:
        self._manager = manager if manager is not None else RegionManager()

        if not isinstance(self._manager, RegionManager):
            raise TypeError("manager must be a RegionManager")

        self._context: ApplicationContext | None = None
        self._dispatcher: QueryDispatcher | None = None
        self._registered_queries: list[type] = []
        self._initialized = False
        self._running = False

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            module_id="region_manager",
            name="Region Manager",
            version="1.0.0",
        )

    @property
    def manager(self) -> RegionManager:
        """Return the manager owned by this module."""

        return self._manager

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def is_running(self) -> bool:
        return self._running

    def initialize(self, context: ApplicationContext) -> None:
        if self._initialized:
            raise RuntimeError("Region Manager module is already initialized")

        if not isinstance(context, ApplicationContext):
            raise TypeError("context must be an ApplicationContext")

        dispatcher = context.get_service(QueryDispatcher)

        if not isinstance(dispatcher, QueryDispatcher):
            raise RuntimeError("QueryDispatcher is not registered in the application")

        if context.services.is_registered(RegionManager):
            raise RuntimeError("A RegionManager service is already registered")

        handlers = (
            (
                GetGeographicRegionQuery,
                GetGeographicRegionHandler(self._manager),
            ),
            (
                ListGeographicRegionsQuery,
                ListGeographicRegionsHandler(self._manager),
            ),
            (
                FindRegionsContainingQuery,
                FindRegionsContainingHandler(self._manager),
            ),
        )

        registered: list[type] = []
        service_registered = False

        try:
            context.services.register(RegionManager, self._manager)
            service_registered = True

            for query_type, handler in handlers:
                if dispatcher.is_registered(query_type):
                    raise RuntimeError(
                        f"Query handler for {query_type.__name__} is already registered"
                    )

                dispatcher.register(query_type, handler)
                registered.append(query_type)

        except Exception:
            for query_type in reversed(registered):
                dispatcher.unregister(query_type)

            if service_registered:
                context.services.unregister(RegionManager)

            raise

        self._context = context
        self._dispatcher = dispatcher
        self._registered_queries = registered
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            raise RuntimeError("Region Manager module is not initialized")

        if self._running:
            raise RuntimeError("Region Manager module is already running")

        self._running = True

    def update(self, delta_time: float) -> None:
        if not self._running:
            raise RuntimeError("Region Manager module is not running")

        if isinstance(delta_time, bool) or not isinstance(delta_time, (int, float)):
            raise TypeError("delta_time must be a number")

        if not isfinite(delta_time) or delta_time < 0:
            raise ValueError("delta_time must be finite and non-negative")

    def stop(self) -> None:
        if not self._initialized:
            raise RuntimeError("Region Manager module is not initialized")

        self._running = False

    def shutdown(self) -> None:
        if not self._initialized:
            return

        if self._running:
            self.stop()

        if self._dispatcher is not None:
            for query_type in reversed(self._registered_queries):
                self._dispatcher.unregister(query_type)

        if self._context is not None:
            self._context.services.unregister(RegionManager)

        self._registered_queries.clear()
        self._dispatcher = None
        self._context = None
        self._initialized = False
        self._running = False
