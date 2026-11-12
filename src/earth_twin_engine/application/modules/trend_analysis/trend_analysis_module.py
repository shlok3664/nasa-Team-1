"""Application module for scientific trend analysis."""

from math import isfinite

from earth_twin_engine.application.commands import CommandDispatcher
from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.application_module import ApplicationModule
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.time_series_management import (
    TimeSeriesManager,
)

from .commands import AnalyzeTimeSeriesTrendCommand
from .trend_analysis_handler import TrendAnalysisHandler
from .trend_analyzer import TrendAnalyzer


class TrendAnalysisModule(ApplicationModule):
    """Integrates statistical trend analysis into the application runtime."""

    def __init__(self, significance_level: float = 0.05) -> None:
        self._analyzer = TrendAnalyzer(significance_level)
        self._context: ApplicationContext | None = None
        self._manager: TimeSeriesManager | None = None
        self._command_dispatcher: CommandDispatcher | None = None
        self._handler: TrendAnalysisHandler | None = None
        self._initialized = False
        self._running = False

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            module_id="trend_analysis",
            name="Trend Analysis",
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
    def analyzer(self) -> TrendAnalyzer:
        return self._analyzer

    @property
    def handler(self) -> TrendAnalysisHandler | None:
        return self._handler

    def initialize(self, context: ApplicationContext) -> None:
        if self._initialized:
            raise RuntimeError("TrendAnalysisModule is already initialized.")

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

        if command_dispatcher.is_registered(AnalyzeTimeSeriesTrendCommand):
            raise RuntimeError("A handler for AnalyzeTimeSeriesTrendCommand is already registered.")

        handler = TrendAnalysisHandler(
            manager=manager,
            analyzer=self._analyzer,
            event_dispatcher=event_dispatcher,
        )

        command_dispatcher.register(AnalyzeTimeSeriesTrendCommand, handler.handle)

        self._context = context
        self._manager = manager
        self._command_dispatcher = command_dispatcher
        self._handler = handler
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            raise RuntimeError("TrendAnalysisModule must be initialized before start.")

        if self._running:
            raise RuntimeError("TrendAnalysisModule is already running.")

        self._running = True

    def update(self, delta_time: float) -> None:
        if not self._initialized:
            raise RuntimeError("TrendAnalysisModule is not initialized.")

        if not isinstance(delta_time, (int, float)) or isinstance(delta_time, bool):
            raise TypeError("delta_time must be numeric.")

        if not isfinite(delta_time) or delta_time < 0.0:
            raise ValueError("delta_time must be finite and non-negative.")

    def stop(self) -> None:
        if not self._initialized:
            raise RuntimeError("TrendAnalysisModule is not initialized.")

        self._running = False

    def shutdown(self) -> None:
        if self._command_dispatcher is not None:
            if self._command_dispatcher.is_registered(AnalyzeTimeSeriesTrendCommand):
                self._command_dispatcher.unregister(AnalyzeTimeSeriesTrendCommand)

        self._handler = None
        self._manager = None
        self._command_dispatcher = None
        self._context = None
        self._running = False
        self._initialized = False
