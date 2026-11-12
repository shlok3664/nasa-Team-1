"""Tests for the visualization application module."""

import pytest

from earth_twin_engine.application.core.application_configuration import ApplicationConfiguration
from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.service_registry import ServiceRegistry
from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.visualization import (
    VisualizationFailedEvent,
    VisualizationModule,
    VisualizationReadyEvent,
    VisualizationService,
)


def test_module_exposes_metadata() -> None:
    module = VisualizationModule()

    assert module.metadata.module_id == "visualization"
    assert module.metadata.name == "Visualization"
    assert module.metadata.version == "1.0.0"
    assert module.metadata.dependencies == ("trend_analysis", "statistical_testing", "regional_comparison")


def test_module_starts_uninitialized() -> None:
    module = VisualizationModule()

    assert module.is_initialized is False
    assert module.is_running is False
    assert isinstance(module.service, VisualizationService)


def test_module_rejects_start_before_initialization() -> None:
    module = VisualizationModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.start()


def test_ready_event_rejects_invalid_source_event() -> None:
    with pytest.raises(TypeError, match="source_event_id"):
        VisualizationReadyEvent(
            source_event_id=None,  # type: ignore[arg-type]
            source_event_type="TrendAnalysisCompletedEvent",
        )


def test_module_can_initialize_and_shutdown() -> None:
    services = ServiceRegistry()
    services.register(EventDispatcher, EventDispatcher())
    context = ApplicationContext(
        configuration=ApplicationConfiguration(application_name="EarthTwinEngine"),
        services=services,
    )

    module = VisualizationModule()
    module.initialize(context)
    assert module.is_initialized is True

    module.start()
    assert module.is_running is True

    module.stop()
    module.shutdown()
    assert module.is_initialized is False
    assert module.is_running is False
