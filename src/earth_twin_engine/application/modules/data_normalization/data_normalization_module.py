"""Application module coordinating scientific data normalization."""

from math import isfinite

from earth_twin_engine.application.commands import CommandDispatcher
from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.application_module import ApplicationModule
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.events import EventDispatcher

from .commands import NormalizeDatasetCommand
from .data_normalization_handler import DataNormalizationHandler
from .data_normalizer import DataNormalizer


class DataNormalizationModule(ApplicationModule):
    """Coordinates scientific dataset normalization."""

    def __init__(self) -> None:
        self._metadata = ModuleMetadata(
            module_id="data_normalization",
            name="Data Normalization",
            version="1.0.0",
            dependencies=("data_validation",),
        )
        self._context: ApplicationContext | None = None
        self._dispatcher: CommandDispatcher | None = None
        self._normalizer: DataNormalizer | None = None
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
            raise RuntimeError("Data Normalization module is already initialized")

        command_dispatcher = context.get_service(CommandDispatcher)
        event_dispatcher = context.get_service(EventDispatcher)

        if not isinstance(command_dispatcher, CommandDispatcher):
            raise RuntimeError("CommandDispatcher is not registered in the application")

        if not isinstance(event_dispatcher, EventDispatcher):
            raise RuntimeError("EventDispatcher is not registered in the application")

        if command_dispatcher.is_registered(NormalizeDatasetCommand):
            raise RuntimeError("A handler for NormalizeDatasetCommand is already registered")

        normalizer = DataNormalizer()
        handler = DataNormalizationHandler(
            normalizer=normalizer,
            event_dispatcher=event_dispatcher,
        )

        try:
            command_dispatcher.register(NormalizeDatasetCommand, handler)
        except Exception:
            if command_dispatcher.is_registered(NormalizeDatasetCommand):
                command_dispatcher.unregister(NormalizeDatasetCommand)
            raise

        self._context = context
        self._dispatcher = command_dispatcher
        self._normalizer = normalizer
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            raise RuntimeError("Data Normalization module is not initialized")

        if self._running:
            raise RuntimeError("Data Normalization module is already running")

        self._running = True

    def update(self, delta_time: float) -> None:
        if isinstance(delta_time, bool) or not isinstance(delta_time, (int, float)):
            raise TypeError("delta_time must be numeric")

        if not isfinite(delta_time) or delta_time < 0:
            raise ValueError("delta_time must be finite and non-negative")

        if not self._running:
            raise RuntimeError("Data Normalization module is not running")

    def stop(self) -> None:
        if not self._initialized:
            raise RuntimeError("Data Normalization module is not initialized")

        self._running = False

    def shutdown(self) -> None:
        if not self._initialized:
            return

        if self._running:
            self.stop()

        if self._dispatcher is not None:
            self._dispatcher.unregister(NormalizeDatasetCommand)

        self._dispatcher = None
        self._context = None
        self._normalizer = None
        self._initialized = False
        self._running = False
