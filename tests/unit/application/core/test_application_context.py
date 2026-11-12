"""Tests for the shared application context."""

from dataclasses import FrozenInstanceError

import pytest

from earth_twin_engine.application.core import (
    ApplicationConfiguration,
    ApplicationContext,
    ServiceRegistry,
)


class DatabaseService:
    """Example database service."""


class LoggingService:
    """Example logging service."""


@pytest.fixture
def configuration() -> ApplicationConfiguration:
    return ApplicationConfiguration(
        application_name="Earth Twin Engine",
        environment="testing",
        debug=True,
    )


@pytest.fixture
def services() -> ServiceRegistry:
    registry = ServiceRegistry()
    registry.register(DatabaseService, DatabaseService())
    return registry


@pytest.fixture
def context(
    configuration: ApplicationConfiguration,
    services: ServiceRegistry,
) -> ApplicationContext:
    return ApplicationContext(
        configuration=configuration,
        services=services,
    )


def test_create_application_context(
    context: ApplicationContext,
    configuration: ApplicationConfiguration,
    services: ServiceRegistry,
) -> None:
    assert context.configuration is configuration
    assert context.services is services


def test_resolve_service_through_context(
    context: ApplicationContext,
    services: ServiceRegistry,
) -> None:
    database = context.resolve(DatabaseService)

    assert database is services.resolve(DatabaseService)


def test_get_registered_service_through_context(
    context: ApplicationContext,
    services: ServiceRegistry,
) -> None:
    database = context.get_service(DatabaseService)

    assert database is services.get(DatabaseService)


def test_get_missing_service_through_context(
    context: ApplicationContext,
) -> None:
    assert context.get_service(LoggingService) is None


def test_resolve_missing_service_through_context(
    context: ApplicationContext,
) -> None:
    with pytest.raises(KeyError, match="not registered"):
        context.resolve(LoggingService)


def test_reject_invalid_configuration() -> None:
    with pytest.raises(
        TypeError,
        match="ApplicationConfiguration",
    ):
        ApplicationContext(
            configuration="invalid",  # type: ignore[arg-type]
            services=ServiceRegistry(),
        )


def test_reject_invalid_service_registry() -> None:
    with pytest.raises(TypeError, match="ServiceRegistry"):
        ApplicationContext(
            configuration=ApplicationConfiguration(
                application_name="Earth Twin Engine",
            ),
            services={},  # type: ignore[arg-type]
        )


def test_application_context_is_immutable(
    context: ApplicationContext,
) -> None:
    with pytest.raises(FrozenInstanceError):
        context.configuration = ApplicationConfiguration(
            application_name="Modified",
        )  # type: ignore[misc]


def test_context_shares_the_same_service_registry(
    context: ApplicationContext,
) -> None:
    logger = LoggingService()

    context.services.register(LoggingService, logger)

    assert context.resolve(LoggingService) is logger
