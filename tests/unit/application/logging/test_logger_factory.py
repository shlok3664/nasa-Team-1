"""Tests for the logger factory."""

import logging
from pathlib import Path
from uuid import uuid4

import pytest

from earth_twin_engine.application.logging import (
    ApplicationLogger,
    LoggerFactory,
    LoggingConfiguration,
    LogLevel,
)


@pytest.fixture
def factory() -> LoggerFactory:
    """Create a logger factory with console logging enabled."""
    return LoggerFactory(
        LoggingConfiguration(
            level=LogLevel.DEBUG,
            console_enabled=True,
            file_enabled=False,
        )
    )


def test_create_logger(factory: LoggerFactory) -> None:
    logger = factory.get_logger("test.application")

    assert logger.name == "test.application"
    assert isinstance(logger, ApplicationLogger)


def test_logger_is_cached(factory: LoggerFactory) -> None:
    first_logger = factory.get_logger("test.cached")
    second_logger = factory.get_logger("test.cached")

    assert first_logger is second_logger


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        " ",
        None,
        123,
    ],
)
def test_reject_invalid_logger_name(
    factory: LoggerFactory,
    invalid_name: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        factory.get_logger(invalid_name)


def test_create_file_logger(tmp_path: Path) -> None:
    log_path = tmp_path / "logs" / "application.log"

    factory = LoggerFactory(
        LoggingConfiguration(
            console_enabled=False,
            file_enabled=True,
            file_path=log_path,
        )
    )

    logger = factory.get_logger(f"test.file.{uuid4().hex}")
    logger.info("Application started")

    underlying_logger = logging.getLogger(logger.name)

    for handler in underlying_logger.handlers:
        handler.flush()

    assert log_path.exists()
    assert "Application started" in log_path.read_text(encoding="utf-8")


def test_configuration_is_exposed(factory: LoggerFactory) -> None:
    assert factory.configuration.level == LogLevel.DEBUG
    assert factory.configuration.console_enabled is True
    assert factory.configuration.file_enabled is False
