"""Application module that converts scientific events into visualization-ready payloads."""

from __future__ import annotations

from math import isfinite

from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.application_module import ApplicationModule
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.regional_comparison.events import (
    RegionalComparisonCompletedEvent,
)
from earth_twin_engine.application.modules.statistical_testing.events import (
    StatisticalTestCompletedEvent,
)
from earth_twin_engine.application.modules.trend_analysis.events import (
    TrendAnalysisCompletedEvent,
)

from .events import VisualizationFailedEvent, VisualizationReadyEvent
from .visualization_service import VisualizationService


class VisualizationModule(ApplicationModule):
    """Publishes visualization-ready payloads when analytical events complete."""

    def __init__(self) -> None:
        self._context: ApplicationContext | None = None
        self._event_dispatcher: EventDispatcher | None = None
        self._service = VisualizationService()
        self._subscriptions: list[object] = []
        self._initialized = False
        self._running = False

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            module_id="visualization",
            name="Visualization",
            version="1.0.0",
            dependencies=("trend_analysis", "statistical_testing", "regional_comparison"),
        )

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def service(self) -> VisualizationService:
        return self._service

    def initialize(self, context: ApplicationContext) -> None:
        if self._initialized:
            raise RuntimeError("VisualizationModule is already initialized.")

        if not isinstance(context, ApplicationContext):
            raise TypeError("context must be an ApplicationContext.")

        event_dispatcher = context.get_service(EventDispatcher)
        if not isinstance(event_dispatcher, EventDispatcher):
            raise RuntimeError("EventDispatcher is not registered.")

        self._context = context
        self._event_dispatcher = event_dispatcher

        self._subscriptions = [
            event_dispatcher.subscribe(TrendAnalysisCompletedEvent, self._handle_event),
            event_dispatcher.subscribe(StatisticalTestCompletedEvent, self._handle_event),
            event_dispatcher.subscribe(RegionalComparisonCompletedEvent, self._handle_event),
        ]
        self._initialized = True

    def _handle_event(self, event):
        if self._event_dispatcher is None:
            raise RuntimeError("VisualizationModule is not initialized.")

        try:
            result = self._service.build_visualization_from_event(event)
            self._event_dispatcher.publish(
                VisualizationReadyEvent(
                    source_event_id=event.event_id,
                    source_event_type=type(event).__name__,
                    correlation_id=event.correlation_id,
                    result=result,
                )
            )
            return result
        except Exception as exc:
            self._event_dispatcher.publish(
                VisualizationFailedEvent(
                    source_event_id=event.event_id,
                    source_event_type=type(event).__name__,
                    correlation_id=event.correlation_id,
                    error_type=type(exc).__name__,
                    error_message=str(exc) or type(exc).__name__,
                )
            )
            raise

    def start(self) -> None:
        if not self._initialized:
            raise RuntimeError("VisualizationModule must be initialized before start.")

        if self._running:
            raise RuntimeError("VisualizationModule is already running.")

        self._running = True

    def update(self, delta_time: float) -> None:
        if not self._initialized:
            raise RuntimeError("VisualizationModule is not initialized.")

        if isinstance(delta_time, bool) or not isinstance(delta_time, (int, float)):
            raise TypeError("delta_time must be numeric.")

        if not isfinite(delta_time) or delta_time < 0.0:
            raise ValueError("delta_time must be finite and non-negative.")

    def stop(self) -> None:
        if not self._initialized:
            raise RuntimeError("VisualizationModule is not initialized.")

        self._running = False

    def shutdown(self) -> None:
        if self._event_dispatcher is not None:
            for subscription in self._subscriptions:
                self._event_dispatcher.unsubscribe(subscription)

        self._subscriptions = []
        self._event_dispatcher = None
        self._context = None
        self._running = False
        self._initialized = False
