"""Configuration for application logging."""

from dataclasses import dataclass
from pathlib import Path

from earth_twin_engine.application.logging.log_level import LogLevel


@dataclass(frozen=True, slots=True)
class LoggingConfiguration:
    """Defines how application logs are generated and written."""

    level: LogLevel = LogLevel.INFO
    console_enabled: bool = True
    file_enabled: bool = False
    file_path: Path | None = None
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"

    def __post_init__(self) -> None:
        if not isinstance(self.level, LogLevel):
            raise TypeError("level must be a LogLevel")

        if not isinstance(self.console_enabled, bool):
            raise TypeError("console_enabled must be a boolean")

        if not isinstance(self.file_enabled, bool):
            raise TypeError("file_enabled must be a boolean")

        if self.file_path is not None and not isinstance(self.file_path, Path):
            raise TypeError("file_path must be a Path or None")

        if self.file_enabled and self.file_path is None:
            raise ValueError("file_path is required when file logging is enabled")

        if not isinstance(self.log_format, str) or not self.log_format.strip():
            raise ValueError("log_format must be a non-empty string")

        if not isinstance(self.date_format, str) or not self.date_format.strip():
            raise ValueError("date_format must be a non-empty string")

        if not self.console_enabled and not self.file_enabled:
            raise ValueError("At least one logging output must be enabled")
