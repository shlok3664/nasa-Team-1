"""Application module for data source registration and routing."""

from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.application_module import ApplicationModule
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.queries import QueryDispatcher

from .data_source_manager import DataSourceManager
from .queries import (
    FindCompatibleDataSourcesQuery,
    GetDataSourceQuery,
    ListDataSourcesQuery,
)
from .query_handlers import (
    FindCompatibleDataSourcesHandler,
    GetDataSourceHandler,
    ListDataSourcesHandler,
)


class DataSourceManagerModule(ApplicationModule):
    """Owns the application-wide data source manager."""

    def __init__(self, manager: DataSourceManager | None = None) -> None:
        self._manager = manager if manager is not None else DataSourceManager()
        if not isinstance(self._manager, DataSourceManager):
            raise TypeError("manager must be a DataSourceManager")

        self._context: ApplicationContext | None = None
        self._dispatcher: QueryDispatcher | None = None
        self._registered_queries: list[type] = []
        self._initialized = False
        self._running = False

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            module_id="data_source_manager",
            name="Data Source Manager",
            version="1.0.0",
        )

    @property
    def manager(self) -> DataSourceManager:
        return self._manager

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def is_running(self) -> bool:
        return self._running

    def initialize(self, context: ApplicationContext) -> None:
        if self._initialized:
            raise RuntimeError("Data Source Manager module is already initialized")
        if not isinstance(context, ApplicationContext):
            raise TypeError("context must be an ApplicationContext")

        dispatcher = context.get_service(QueryDispatcher)
        if not isinstance(dispatcher, QueryDispatcher):
            raise RuntimeError("QueryDispatcher is not registered in the application")

        if context.services.is_registered(DataSourceManager):
            raise RuntimeError("A DataSourceManager service is already registered")

        handlers = (
            (GetDataSourceQuery, GetDataSourceHandler(self._manager)),
            (ListDataSourcesQuery, ListDataSourcesHandler(self._manager)),
            (
                FindCompatibleDataSourcesQuery,
                FindCompatibleDataSourcesHandler(self._manager),
            ),
        )

        registered: list[type] = []
        service_registered = False

        try:
            context.services.register(DataSourceManager, self._manager)
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
                context.services.unregister(DataSourceManager)
            raise

        self._context = context
        self._dispatcher = dispatcher
        self._registered_queries = registered
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            raise RuntimeError("Data Source Manager module is not initialized")
        if self._running:
            raise RuntimeError("Data Source Manager module is already running")
        self._running = True

    def update(self, delta_time: float) -> None:
        if not self._running:
            raise RuntimeError("Data Source Manager module is not running")
        if isinstance(delta_time, bool) or not isinstance(delta_time, (int, float)):
            raise TypeError("delta_time must be a number")
        if delta_time < 0:
            raise ValueError("delta_time must not be negative")

    def stop(self) -> None:
        if not self._initialized:
            raise RuntimeError("Data Source Manager module is not initialized")
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
            self._context.services.unregister(DataSourceManager)

        self._registered_queries.clear()
        self._dispatcher = None
        self._context = None
        self._initialized = False
        self._running = False
