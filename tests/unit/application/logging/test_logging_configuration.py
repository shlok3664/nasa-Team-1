from pathlib import Path

import pytest

from earth_twin_engine.application.logging import (
    LoggingConfiguration,
    LogLevel,
)


def test_default_configuration() -> None:
    configuration = LoggingConfiguration()

    assert configuration.level is LogLevel.INFO
    assert configuration.console_enabled
    assert not configuration.file_enabled
    assert configuration.file_path is None


def test_accept_custom_configuration(tmp_path: Path) -> None:
    log_path = tmp_path / "logs" / "application.log"

    configuration = LoggingConfiguration(
        level=LogLevel.DEBUG,
        console_enabled=False,
        file_enabled=True,
        file_path=log_path,
    )

    assert configuration.level is LogLevel.DEBUG
    assert configuration.file_enabled
    assert configuration.file_path == log_path


def test_reject_invalid_level() -> None:
    with pytest.raises(TypeError):
        LoggingConfiguration(level=20)


@pytest.mark.parametrize(
    "field,value",
    [
        ("console_enabled", "yes"),
        ("file_enabled", 1),
    ],
)
def test_reject_invalid_output_flags(field: str, value: object) -> None:
    with pytest.raises(TypeError):
        LoggingConfiguration(**{field: value})


def test_reject_missing_file_path() -> None:
    with pytest.raises(ValueError):
        LoggingConfiguration(file_enabled=True)


def test_reject_invalid_file_path() -> None:
    with pytest.raises(TypeError):
        LoggingConfiguration(file_path="application.log")


def test_reject_empty_log_format() -> None:
    with pytest.raises(ValueError):
        LoggingConfiguration(log_format=" ")


def test_reject_empty_date_format() -> None:
    with pytest.raises(ValueError):
        LoggingConfiguration(date_format="")


def test_reject_disabled_outputs() -> None:
    with pytest.raises(ValueError):
        LoggingConfiguration(
            console_enabled=False,
            file_enabled=False,
        )
