"""Application module coordinating Earth science dataset acquisition."""

from math import isfinite

from earth_twin_engine.application.commands import CommandDispatcher
from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.application_module import ApplicationModule
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.data_source_manager.data_source_manager import (
    DataSourceManager,
)
from earth_twin_engine.application.modules.region_manager.region_manager import (
    RegionManager,
)
from earth_twin_engine.application.modules.variable_discovery.variable_catalog import (
    VariableCatalog,
)

from .commands import AcquireDatasetCommand
from .data_acquisition_handler import DataAcquisitionHandler


class DataAcquisitionModule(ApplicationModule):
    """Coordinates acquisition using the existing application managers."""

    def __init__(self) -> None:
        self._metadata = ModuleMetadata(
            module_id="data_acquisition",
            name="Data Acquisition",
            version="1.0.0",
            dependencies=(
                "variable_discovery",
                "region_manager",
                "data_source_manager",
            ),
        )
        self._context: ApplicationContext | None = None
        self._dispatcher: CommandDispatcher | None = None
        self._initialized = False
        self._running = False

    @property
    def metadata(self) -> ModuleMetadata:
        return self._metadata

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
            raise RuntimeError("Data Acquisition module is already initialized")

        command_dispatcher = context.get_service(CommandDispatcher)
        event_dispatcher = context.get_service(EventDispatcher)
        variable_catalog = context.get_service(VariableCatalog)
        region_manager = context.get_service(RegionManager)
        data_source_manager = context.get_service(DataSourceManager)

        if not isinstance(command_dispatcher, CommandDispatcher):
            raise RuntimeError("CommandDispatcher is not registered in the application")

        if not isinstance(event_dispatcher, EventDispatcher):
            raise RuntimeError("EventDispatcher is not registered in the application")

        if not isinstance(variable_catalog, VariableCatalog):
            raise RuntimeError("VariableCatalog is not registered in the application")

        if not isinstance(region_manager, RegionManager):
            raise RuntimeError("RegionManager is not registered in the application")

        if not isinstance(data_source_manager, DataSourceManager):
            raise RuntimeError("DataSourceManager is not registered in the application")

        if command_dispatcher.is_registered(AcquireDatasetCommand):
            raise RuntimeError("A handler for AcquireDatasetCommand is already registered")

        handler = DataAcquisitionHandler(
            variable_catalog=variable_catalog,
            region_manager=region_manager,
            data_source_manager=data_source_manager,
            event_dispatcher=event_dispatcher,
        )

        command_dispatcher.register(AcquireDatasetCommand, handler)

        self._context = context
        self._dispatcher = command_dispatcher
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            raise RuntimeError("Data Acquisition module is not initialized")

        if self._running:
            raise RuntimeError("Data Acquisition module is already running")

        self._running = True

    def update(self, delta_time: float) -> None:
        if isinstance(delta_time, bool) or not isinstance(delta_time, (int, float)):
            raise TypeError("delta_time must be numeric")

        if not isfinite(delta_time) or delta_time < 0:
            raise ValueError("delta_time must be finite and non-negative")

        if not self._running:
            raise RuntimeError("Data Acquisition module is not running")

    def stop(self) -> None:
        if not self._initialized:
            raise RuntimeError("Data Acquisition module is not initialized")

        self._running = False

    def shutdown(self) -> None:
        if not self._initialized:
            return

        if self._running:
            self.stop()

        if self._dispatcher is not None:
            self._dispatcher.unregister(AcquireDatasetCommand)

        self._dispatcher = None
        self._context = None
        self._initialized = False
        self._running = False
