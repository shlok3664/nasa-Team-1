"""Tests for the application service registry."""

import pytest

from earth_twin_engine.application.core import ServiceRegistry


class DatabaseService:
    """Example database service."""

    def execute(self) -> str:
        return "executed"


class LoggingService:
    """Example logging service."""


class DatabaseServiceImplementation(DatabaseService):
    """Concrete implementation of the database service."""


def test_register_and_resolve_service() -> None:
    registry = ServiceRegistry()
    database = DatabaseService()

    registry.register(DatabaseService, database)

    assert registry.resolve(DatabaseService) is database


def test_register_multiple_services() -> None:
    registry = ServiceRegistry()
    database = DatabaseService()
    logger = LoggingService()

    registry.register(DatabaseService, database)
    registry.register(LoggingService, logger)

    assert registry.resolve(DatabaseService) is database
    assert registry.resolve(LoggingService) is logger
    assert registry.service_count == 2


def test_register_subclass_instance_under_base_type() -> None:
    registry = ServiceRegistry()
    database = DatabaseServiceImplementation()

    registry.register(DatabaseService, database)

    assert registry.resolve(DatabaseService) is database


def test_reject_duplicate_registration() -> None:
    registry = ServiceRegistry()

    registry.register(DatabaseService, DatabaseService())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(DatabaseService, DatabaseService())


def test_reject_instance_with_wrong_type() -> None:
    registry = ServiceRegistry()

    with pytest.raises(TypeError, match="match the registered service type"):
        registry.register(DatabaseService, LoggingService())  # type: ignore[arg-type]


def test_resolve_missing_service_raises_key_error() -> None:
    registry = ServiceRegistry()

    with pytest.raises(KeyError, match="not registered"):
        registry.resolve(DatabaseService)


def test_get_missing_service_returns_none() -> None:
    registry = ServiceRegistry()

    assert registry.get(DatabaseService) is None


def test_get_registered_service() -> None:
    registry = ServiceRegistry()
    database = DatabaseService()

    registry.register(DatabaseService, database)

    assert registry.get(DatabaseService) is database


def test_check_registration_status() -> None:
    registry = ServiceRegistry()

    assert registry.is_registered(DatabaseService) is False

    registry.register(DatabaseService, DatabaseService())

    assert registry.is_registered(DatabaseService) is True


def test_service_count_tracks_registrations() -> None:
    registry = ServiceRegistry()

    assert registry.service_count == 0

    registry.register(DatabaseService, DatabaseService())

    assert registry.service_count == 1

    registry.register(LoggingService, LoggingService())

    assert registry.service_count == 2


@pytest.mark.parametrize(
    "invalid_service_type",
    ["DatabaseService", 123, None],
)
def test_reject_invalid_service_type(
    invalid_service_type: object,
) -> None:
    registry = ServiceRegistry()

    with pytest.raises(TypeError, match="service_type"):
        registry.resolve(invalid_service_type)  # type: ignore[arg-type]


def test_registered_service_can_execute() -> None:
    registry = ServiceRegistry()
    registry.register(DatabaseService, DatabaseService())

    database = registry.resolve(DatabaseService)

    assert database.execute() == "executed"
