"""Loads application configuration from JSON and environment variables."""

import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from earth_twin_engine.application.core.application_configuration import (
    ApplicationConfiguration,
)


class ApplicationConfigurationLoader:
    """Builds application configuration from supported configuration sources."""

    ENVIRONMENT_PREFIX = "ETE_"

    _ALLOWED_FIELDS = frozenset(
        {
            "application_name",
            "environment",
            "debug",
            "settings",
        }
    )

    def load(
        self,
        config_path: str | Path | None = None,
        environ: Mapping[str, str] | None = None,
    ) -> ApplicationConfiguration:
        """Load JSON configuration and apply environment-variable overrides."""

        configuration_data: dict[str, Any] = {}

        if config_path is not None:
            path = Path(config_path)
            configuration_data = self._load_json(path)

        self._validate_fields(configuration_data)

        environment = os.environ if environ is None else environ

        application_name = configuration_data.get(
            "application_name",
            "Earth Twin Engine",
        )
        application_environment = configuration_data.get(
            "environment",
            "development",
        )
        debug = configuration_data.get("debug", False)
        settings = configuration_data.get("settings", {})

        application_name = environment.get(
            f"{self.ENVIRONMENT_PREFIX}APPLICATION_NAME",
            application_name,
        )
        application_environment = environment.get(
            f"{self.ENVIRONMENT_PREFIX}ENVIRONMENT",
            application_environment,
        )

        debug_override = environment.get(f"{self.ENVIRONMENT_PREFIX}DEBUG")
        if debug_override is not None:
            debug = self._parse_boolean(debug_override)

        if not isinstance(settings, Mapping):
            raise TypeError("configuration settings must be a mapping")

        return ApplicationConfiguration(
            application_name=application_name,
            environment=application_environment,
            debug=debug,
            settings=settings,
        )

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        """Read and validate the root structure of a JSON configuration file."""

        content = path.read_text(encoding="utf-8")
        data = json.loads(content)

        if not isinstance(data, dict):
            raise TypeError("configuration file must contain a JSON object")

        return data

    def _validate_fields(self, data: Mapping[str, Any]) -> None:
        """Reject unsupported configuration fields."""

        unknown_fields = set(data) - self._ALLOWED_FIELDS

        if unknown_fields:
            names = ", ".join(sorted(unknown_fields))
            raise ValueError(f"unknown configuration field(s): {names}")

    @staticmethod
    def _parse_boolean(value: str) -> bool:
        """Parse a strict environment-variable boolean."""

        normalized = value.strip().lower()

        if normalized in {"1", "true", "yes", "on"}:
            return True

        if normalized in {"0", "false", "no", "off"}:
            return False

        raise ValueError(f"invalid boolean environment value: {value!r}")
