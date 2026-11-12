"""Tests for the scientific interpretation application module."""

import pytest

from earth_twin_engine.application.core.application_configuration import ApplicationConfiguration
from earth_twin_engine.application.core.application_context import ApplicationContext
from earth_twin_engine.application.core.service_registry import ServiceRegistry
from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.scientific_interpretation import (
    ScientificInterpretation,
    ScientificInterpretationFailedEvent,
    ScientificInterpretationModule,
    ScientificInterpretationService,
)


def test_module_exposes_metadata() -> None:
    module = ScientificInterpretationModule()

    assert module.metadata.module_id == "scientific_interpretation"
    assert module.metadata.name == "Scientific Interpretation"
    assert module.metadata.version == "1.0.0"
    assert module.metadata.dependencies == ("trend_analysis", "statistical_testing", "regional_comparison")


def test_module_starts_uninitialized() -> None:
    module = ScientificInterpretationModule()

    assert module.is_initialized is False
    assert module.is_running is False
    assert isinstance(module.service, ScientificInterpretationService)


def test_module_rejects_start_before_initialization() -> None:
    module = ScientificInterpretationModule()

    with pytest.raises(RuntimeError, match="initialized"):
        module.start()


def test_failed_event_rejects_invalid_error_type() -> None:
    with pytest.raises(ValueError, match="error_type"):
        ScientificInterpretationFailedEvent(
            source_event_id=None,
            source_event_type="TrendAnalysisCompletedEvent",
            error_type=" ",
            error_message="cannot interpret",
        )


def test_module_can_initialize_and_shutdown() -> None:
    services = ServiceRegistry()
    services.register(EventDispatcher, EventDispatcher())
    context = ApplicationContext(
        configuration=ApplicationConfiguration(application_name="EarthTwinEngine"),
        services=services,
    )

    module = ScientificInterpretationModule()
    module.initialize(context)
    assert module.is_initialized is True

    module.start()
    assert module.is_running is True

    module.stop()
    module.shutdown()
    assert module.is_initialized is False
    assert module.is_running is False


def test_interpretation_model_validates_non_empty_values() -> None:
    with pytest.raises(ValueError, match="summary"):
        ScientificInterpretation(
            variable_id="temperature",
            summary="",
            observed_pattern="Increasing",
            trend_magnitude="Positive slope",
            statistical_evidence="P-value below threshold",
        )
