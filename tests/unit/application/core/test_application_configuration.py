"""Tests for application configuration."""

from dataclasses import FrozenInstanceError

import pytest

from earth_twin_engine.application.core import ApplicationConfiguration


def test_create_default_configuration() -> None:
    configuration = ApplicationConfiguration(
        application_name="Earth Twin Engine",
    )

    assert configuration.application_name == "Earth Twin Engine"
    assert configuration.environment == "development"
    assert configuration.debug is False
    assert configuration.settings == {}


def test_create_configuration_with_custom_settings() -> None:
    configuration = ApplicationConfiguration(
        application_name="Earth Twin Engine",
        environment="testing",
        debug=True,
        settings={
            "api_port": 8000,
            "data_directory": "data/",
        },
    )

    assert configuration.environment == "testing"
    assert configuration.debug is True
    assert configuration.get_setting("api_port") == 8000
    assert configuration.get_setting("data_directory") == "data/"


def test_get_missing_setting_returns_default() -> None:
    configuration = ApplicationConfiguration(
        application_name="Earth Twin Engine",
    )

    assert configuration.get_setting("missing", 42) == 42
    assert configuration.get_setting("missing") is None


@pytest.mark.parametrize(
    "application_name",
    ["", "   "],
)
def test_reject_empty_application_name(application_name: str) -> None:
    with pytest.raises(ValueError, match="application_name"):
        ApplicationConfiguration(application_name=application_name)


@pytest.mark.parametrize(
    "environment",
    ["", "   "],
)
def test_reject_empty_environment(environment: str) -> None:
    with pytest.raises(ValueError, match="environment"):
        ApplicationConfiguration(
            application_name="Earth Twin Engine",
            environment=environment,
        )


def test_reject_non_boolean_debug() -> None:
    with pytest.raises(TypeError, match="debug"):
        ApplicationConfiguration(
            application_name="Earth Twin Engine",
            debug=1,  # type: ignore[arg-type]
        )


def test_reject_non_mapping_settings() -> None:
    with pytest.raises(TypeError, match="mapping"):
        ApplicationConfiguration(
            application_name="Earth Twin Engine",
            settings=[],  # type: ignore[arg-type]
        )


def test_reject_non_string_setting_key() -> None:
    with pytest.raises(TypeError, match="keys must be strings"):
        ApplicationConfiguration(
            application_name="Earth Twin Engine",
            settings={1: "invalid"},  # type: ignore[dict-item]
        )


def test_reject_empty_setting_key() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        ApplicationConfiguration(
            application_name="Earth Twin Engine",
            settings={" ": "invalid"},
        )


def test_settings_are_read_only() -> None:
    configuration = ApplicationConfiguration(
        application_name="Earth Twin Engine",
        settings={"api_port": 8000},
    )

    with pytest.raises(TypeError):
        configuration.settings["api_port"] = 9000  # type: ignore[index]


def test_original_settings_dictionary_cannot_mutate_configuration() -> None:
    settings = {"api_port": 8000}

    configuration = ApplicationConfiguration(
        application_name="Earth Twin Engine",
        settings=settings,
    )

    settings["api_port"] = 9000

    assert configuration.get_setting("api_port") == 8000


def test_configuration_is_immutable() -> None:
    configuration = ApplicationConfiguration(
        application_name="Earth Twin Engine",
    )

    with pytest.raises(FrozenInstanceError):
        configuration.debug = True  # type: ignore[misc]


def test_get_setting_rejects_non_string_key() -> None:
    configuration = ApplicationConfiguration(
        application_name="Earth Twin Engine",
    )

    with pytest.raises(TypeError, match="setting key"):
        configuration.get_setting(123)  # type: ignore[arg-type]
