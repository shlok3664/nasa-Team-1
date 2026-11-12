import json
from pathlib import Path

import pytest

from earth_twin_engine.application.core import ApplicationConfiguration
from earth_twin_engine.application.launcher import ApplicationConfigurationLoader


@pytest.fixture
def loader() -> ApplicationConfigurationLoader:
    return ApplicationConfigurationLoader()


def test_load_default_configuration(
    loader: ApplicationConfigurationLoader,
) -> None:
    configuration = loader.load(environ={})

    assert isinstance(configuration, ApplicationConfiguration)
    assert configuration.application_name == "Earth Twin Engine"
    assert configuration.environment == "development"
    assert configuration.debug is False
    assert dict(configuration.settings) == {}


def test_load_configuration_from_json(
    loader: ApplicationConfigurationLoader,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "application_name": "ETE Test",
                "environment": "testing",
                "debug": True,
                "settings": {
                    "max_workers": 4,
                    "data_directory": "data",
                },
            }
        ),
        encoding="utf-8",
    )

    configuration = loader.load(config_path, environ={})

    assert configuration.application_name == "ETE Test"
    assert configuration.environment == "testing"
    assert configuration.debug is True
    assert configuration.get_setting("max_workers") == 4
    assert configuration.get_setting("data_directory") == "data"


def test_environment_overrides_json_configuration(
    loader: ApplicationConfigurationLoader,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "application_name": "JSON Name",
                "environment": "development",
                "debug": False,
            }
        ),
        encoding="utf-8",
    )

    configuration = loader.load(
        config_path,
        environ={
            "ETE_APPLICATION_NAME": "Environment Name",
            "ETE_ENVIRONMENT": "production",
            "ETE_DEBUG": "true",
        },
    )

    assert configuration.application_name == "Environment Name"
    assert configuration.environment == "production"
    assert configuration.debug is True


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", True),
        ("true", True),
        ("TRUE", True),
        ("yes", True),
        ("on", True),
        ("0", False),
        ("false", False),
        ("FALSE", False),
        ("no", False),
        ("off", False),
    ],
)
def test_parse_environment_boolean_values(
    loader: ApplicationConfigurationLoader,
    value: str,
    expected: bool,
) -> None:
    configuration = loader.load(
        environ={"ETE_DEBUG": value},
    )

    assert configuration.debug is expected


def test_reject_invalid_environment_boolean(
    loader: ApplicationConfigurationLoader,
) -> None:
    with pytest.raises(ValueError, match="invalid boolean"):
        loader.load(environ={"ETE_DEBUG": "sometimes"})


def test_reject_unknown_configuration_fields(
    loader: ApplicationConfigurationLoader,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"application_name": "ETE", "unknown_option": True}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unknown configuration field"):
        loader.load(config_path, environ={})


def test_reject_non_object_json(
    loader: ApplicationConfigurationLoader,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text('["not", "an", "object"]', encoding="utf-8")

    with pytest.raises(TypeError, match="JSON object"):
        loader.load(config_path, environ={})


def test_reject_invalid_json(
    loader: ApplicationConfigurationLoader,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        loader.load(config_path, environ={})


def test_reject_non_mapping_settings(
    loader: ApplicationConfigurationLoader,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"settings": ["invalid", "settings"]}),
        encoding="utf-8",
    )

    with pytest.raises(TypeError, match="settings must be a mapping"):
        loader.load(config_path, environ={})


def test_reject_missing_configuration_file(
    loader: ApplicationConfigurationLoader,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        loader.load(config_path, environ={})


def test_configuration_settings_remain_immutable(
    loader: ApplicationConfigurationLoader,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"settings": {"max_workers": 4}}),
        encoding="utf-8",
    )

    configuration = loader.load(config_path, environ={})

    with pytest.raises(TypeError):
        configuration.settings["max_workers"] = 8  # type: ignore[index]
