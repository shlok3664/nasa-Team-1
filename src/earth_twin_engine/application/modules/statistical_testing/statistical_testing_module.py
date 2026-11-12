"""Application module for statistical testing."""

from math import isfinite

from earth_twin_engine.application.commands import CommandDispatcher
from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.application_module import ApplicationModule
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.time_series_management import (
    TimeSeriesManager,
)

from .commands import RunStatisticalTestCommand
from .statistical_test import MannKendallTest, OneSampleTTest, WelchTTest
from .statistical_test_registry import StatisticalTestRegistry
from .statistical_testing_handler import StatisticalTestingHandler
from .statistical_testing_service import StatisticalTestingService


class StatisticalTestingModule(ApplicationModule):
    """Integrates statistical tests into the application runtime."""

    def __init__(self, significance_level: float = 0.05) -> None:
        if (
            not isinstance(significance_level, (int, float))
            or isinstance(significance_level, bool)
            or not isfinite(significance_level)
            or not 0.0 < significance_level < 1.0
        ):
            raise ValueError("significance_level must be finite and between 0 and 1.")

        self._significance_level = float(significance_level)
        self._registry = StatisticalTestRegistry()
        self._registry.register(MannKendallTest())
        self._registry.register(OneSampleTTest())
        self._registry.register(WelchTTest())

        self._service = StatisticalTestingService(self._registry)
        self._context: ApplicationContext | None = None
        self._manager: TimeSeriesManager | None = None
        self._command_dispatcher: CommandDispatcher | None = None
        self._handler: StatisticalTestingHandler | None = None
        self._initialized = False
        self._running = False

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            module_id="statistical_testing",
            name="Statistical Testing",
            version="1.0.0",
            dependencies=("time_series_management",),
        )

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def registry(self) -> StatisticalTestRegistry:
        return self._registry

    @property
    def service(self) -> StatisticalTestingService:
        return self._service

    @property
    def handler(self) -> StatisticalTestingHandler | None:
        return self._handler

    def initialize(self, context: ApplicationContext) -> None:
        if self._initialized:
            raise RuntimeError("StatisticalTestingModule is already initialized.")

        if not isinstance(context, ApplicationContext):
            raise TypeError("context must be an ApplicationContext.")

        manager = context.get_service(TimeSeriesManager)
        command_dispatcher = context.get_service(CommandDispatcher)
        event_dispatcher = context.get_service(EventDispatcher)

        if not isinstance(manager, TimeSeriesManager):
            raise RuntimeError("TimeSeriesManager is not registered.")

        if not isinstance(command_dispatcher, CommandDispatcher):
            raise RuntimeError("CommandDispatcher is not registered.")

        if not isinstance(event_dispatcher, EventDispatcher):
            raise RuntimeError("EventDispatcher is not registered.")

        if command_dispatcher.is_registered(RunStatisticalTestCommand):
            raise RuntimeError("A handler for RunStatisticalTestCommand is already registered.")

        handler = StatisticalTestingHandler(
            manager=manager,
            service=self._service,
            event_dispatcher=event_dispatcher,
        )

        command_dispatcher.register(RunStatisticalTestCommand, handler.handle)

        self._context = context
        self._manager = manager
        self._command_dispatcher = command_dispatcher
        self._handler = handler
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            raise RuntimeError("StatisticalTestingModule must be initialized before start.")

        if self._running:
            raise RuntimeError("StatisticalTestingModule is already running.")

        self._running = True

    def update(self, delta_time: float) -> None:
        if not self._initialized:
            raise RuntimeError("StatisticalTestingModule is not initialized.")

        if (
            not isinstance(delta_time, (int, float))
            or isinstance(delta_time, bool)
            or not isfinite(delta_time)
            or delta_time < 0.0
        ):
            raise ValueError("delta_time must be finite and non-negative.")

    def stop(self) -> None:
        if not self._initialized:
            raise RuntimeError("StatisticalTestingModule is not initialized.")

        self._running = False

    def shutdown(self) -> None:
        if self._command_dispatcher is not None and (
            self._command_dispatcher.is_registered(RunStatisticalTestCommand)
        ):
            self._command_dispatcher.unregister(RunStatisticalTestCommand)

        self._handler = None
        self._manager = None
        self._command_dispatcher = None
        self._context = None
        self._running = False
        self._initialized = False
