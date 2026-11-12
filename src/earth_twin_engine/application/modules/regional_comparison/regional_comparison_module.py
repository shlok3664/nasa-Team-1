"""Application module for regional trend comparison."""

from math import isfinite

from earth_twin_engine.application.commands import CommandDispatcher
from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.application_module import ApplicationModule
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.region_manager import RegionManager
from earth_twin_engine.application.modules.time_series_management import TimeSeriesManager
from earth_twin_engine.application.modules.trend_analysis import TrendAnalyzer

from .commands import CompareRegionsCommand
from .regional_comparison_handler import RegionalComparisonHandler
from .regional_comparison_service import RegionalComparisonService


class RegionalComparisonModule(ApplicationModule):
    """Owns regional comparison services and command integration."""

    def __init__(self, significance_level: float = 0.05) -> None:
        if (
            isinstance(significance_level, bool)
            or not isinstance(significance_level, (int, float))
            or not isfinite(significance_level)
            or not 0.0 < significance_level < 1.0
        ):
            raise ValueError("significance_level must be finite and between 0 and 1")

        self._significance_level = float(significance_level)
        self._context: ApplicationContext | None = None
        self._dispatcher: CommandDispatcher | None = None
        self._handler: RegionalComparisonHandler | None = None
        self._service: RegionalComparisonService | None = None
        self._initialized = False
        self._running = False

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            module_id="regional_comparison",
            name="Regional Comparison",
            version="1.0.0",
            dependencies=("region_manager", "time_series_management", "trend_analysis"),
        )

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def service(self) -> RegionalComparisonService:
        if self._service is None:
            raise RuntimeError("Regional Comparison module is not initialized")

        return self._service

    def initialize(self, context: ApplicationContext) -> None:
        if self._initialized:
            raise RuntimeError("Regional Comparison module is already initialized")

        if not isinstance(context, ApplicationContext):
            raise TypeError("context must be an ApplicationContext")

        dispatcher = context.get_service(CommandDispatcher)
        event_dispatcher = context.get_service(EventDispatcher)
        region_manager = context.get_service(RegionManager)
        time_series_manager = context.get_service(TimeSeriesManager)

        if not isinstance(dispatcher, CommandDispatcher):
            raise TypeError("CommandDispatcher service is invalid")

        if not isinstance(event_dispatcher, EventDispatcher):
            raise TypeError("EventDispatcher service is invalid")

        if dispatcher.is_registered(CompareRegionsCommand):
            raise RuntimeError("CompareRegionsCommand is already registered")

        service = RegionalComparisonService(
            region_manager=region_manager,
            time_series_manager=time_series_manager,
            trend_analyzer=TrendAnalyzer(self._significance_level),
        )
        handler = RegionalComparisonHandler(service, event_dispatcher)

        dispatcher.register(CompareRegionsCommand, handler)

        self._context = context
        self._dispatcher = dispatcher
        self._service = service
        self._handler = handler
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            raise RuntimeError("Regional Comparison module is not initialized")

        if self._running:
            raise RuntimeError("Regional Comparison module is already running")

        self._running = True

    def update(self, delta_time: float) -> None:
        if not self._running:
            raise RuntimeError("Regional Comparison module is not running")

        if (
            isinstance(delta_time, bool)
            or not isinstance(delta_time, (int, float))
            or not isfinite(delta_time)
            or delta_time < 0
        ):
            raise ValueError("delta_time must be finite and non-negative")

    def stop(self) -> None:
        if not self._initialized:
            raise RuntimeError("Regional Comparison module is not initialized")

        self._running = False

    def shutdown(self) -> None:
        if not self._initialized:
            return

        if self._running:
            self.stop()

        if self._dispatcher is not None:
            self._dispatcher.unregister(CompareRegionsCommand)

        self._handler = None
        self._service = None
        self._dispatcher = None
        self._context = None
        self._initialized = False
        self._running = False
