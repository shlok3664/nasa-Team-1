"""Application module for scientific time-series management."""

from earth_twin_engine.application.commands import CommandDispatcher
from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.application_module import ApplicationModule
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.time_series_management.aggregation import (
    MissingPeriodDetector,
    SpatialAggregator,
    TemporalAggregator,
)
from earth_twin_engine.application.modules.time_series_management.commands import (
    AggregateSpatialTimeSeriesCommand,
    AggregateTimeSeriesCommand,
    RegisterTimeSeriesCommand,
    RemoveTimeSeriesCommand,
)
from earth_twin_engine.application.modules.time_series_management.time_series_manager import (
    TimeSeriesManager,
)

from .time_series_management_handler import TimeSeriesManagementHandler


class TimeSeriesManagementModule(ApplicationModule):
    """Owns time-series storage, aggregation, and command integration."""

    def __init__(self) -> None:
        self._context: ApplicationContext | None = None
        self._command_dispatcher: CommandDispatcher | None = None
        self._manager: TimeSeriesManager | None = None
        self._handler: TimeSeriesManagementHandler | None = None
        self._registered_commands: tuple[type, ...] = ()
        self._service_registered = False
        self._initialized = False
        self._running = False

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            module_id="time_series_management",
            name="Time-Series Management",
            version="1.0.0",
            dependencies=("data_normalization",),
        )

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def manager(self) -> TimeSeriesManager:
        if self._manager is None:
            raise RuntimeError("time-series management module is not initialized")

        return self._manager

    @property
    def missing_period_detector(self) -> MissingPeriodDetector:
        return MissingPeriodDetector()

    def initialize(self, context: ApplicationContext) -> None:
        if self._initialized:
            raise RuntimeError("time-series management module is already initialized")

        if not isinstance(context, ApplicationContext):
            raise TypeError("context must be an ApplicationContext")

        command_dispatcher = context.get_service(CommandDispatcher)
        event_dispatcher = context.get_service(EventDispatcher)

        if not isinstance(command_dispatcher, CommandDispatcher):
            raise TypeError("CommandDispatcher service is invalid")

        if not isinstance(event_dispatcher, EventDispatcher):
            raise TypeError("EventDispatcher service is invalid")

        manager = TimeSeriesManager()
        handler = TimeSeriesManagementHandler(
            manager=manager,
            temporal_aggregator=TemporalAggregator(),
            spatial_aggregator=SpatialAggregator(),
            event_dispatcher=event_dispatcher,
        )

        command_types = (
            RegisterTimeSeriesCommand,
            RemoveTimeSeriesCommand,
            AggregateTimeSeriesCommand,
            AggregateSpatialTimeSeriesCommand,
        )

        if any(command_dispatcher.is_registered(item) for item in command_types):
            raise RuntimeError("one or more time-series commands are already registered")

        if context.services.is_registered(TimeSeriesManager):
            raise RuntimeError("TimeSeriesManager service is already registered")

        registered: list[type] = []

        try:
            context.services.register(TimeSeriesManager, manager)
            self._service_registered = True

            for command_type in command_types:
                command_dispatcher.register(command_type, handler)
                registered.append(command_type)

        except Exception:
            for command_type in reversed(registered):
                command_dispatcher.unregister(command_type)

            if self._service_registered:
                context.services.unregister(TimeSeriesManager)
                self._service_registered = False

            raise

        self._context = context
        self._command_dispatcher = command_dispatcher
        self._manager = manager
        self._handler = handler
        self._registered_commands = tuple(registered)
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            raise RuntimeError("module must be initialized before starting")

        self._running = True

    def update(self, delta_time: float) -> None:
        if not self._initialized:
            raise RuntimeError("module must be initialized before updating")

        if isinstance(delta_time, bool) or not isinstance(delta_time, (int, float)):
            raise TypeError("delta_time must be a number")

        if delta_time < 0:
            raise ValueError("delta_time cannot be negative")

    def stop(self) -> None:
        self._running = False

    def shutdown(self) -> None:
        if self._command_dispatcher is not None:
            for command_type in reversed(self._registered_commands):
                self._command_dispatcher.unregister(command_type)

        if self._context is not None and self._service_registered:
            self._context.services.unregister(TimeSeriesManager)

        self._registered_commands = ()
        self._service_registered = False
        self._handler = None
        self._manager = None
        self._command_dispatcher = None
        self._context = None
        self._running = False
        self._initialized = False
