"""Application configuration contract."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType


@dataclass(frozen=True, slots=True)
class ApplicationConfiguration:
    """Immutable configuration shared across the application."""

    application_name: str
    environment: str = "development"
    debug: bool = False
    settings: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.application_name, str) or not self.application_name.strip():
            raise ValueError("application_name must be a non-empty string")

        if not isinstance(self.environment, str) or not self.environment.strip():
            raise ValueError("environment must be a non-empty string")

        if not isinstance(self.debug, bool):
            raise TypeError("debug must be a boolean")

        if not isinstance(self.settings, Mapping):
            raise TypeError("settings must be a mapping")

        copied_settings = dict(self.settings)

        for key in copied_settings:
            if not isinstance(key, str):
                raise TypeError("setting keys must be strings")

            if not key.strip():
                raise ValueError("setting keys cannot be empty")

        object.__setattr__(
            self,
            "settings",
            MappingProxyType(copied_settings),
        )

    def get_setting(
        self,
        key: str,
        default: object = None,
    ) -> object:
        """Retrieve a setting, returning the default when it is absent."""

        if not isinstance(key, str):
            raise TypeError("setting key must be a string")

        return self.settings.get(key, default)
