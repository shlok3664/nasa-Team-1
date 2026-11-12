"""Factory for creating configured application loggers."""

import logging
from threading import RLock

from earth_twin_engine.application.logging.application_logger import (
    ApplicationLogger,
)
from earth_twin_engine.application.logging.logging_configuration import (
    LoggingConfiguration,
)


class LoggerFactory:
    """Creates and manages named application loggers."""

    def __init__(
        self,
        configuration: LoggingConfiguration,
    ) -> None:
        if not isinstance(configuration, LoggingConfiguration):
            raise TypeError("configuration must be a LoggingConfiguration")

        self._configuration = configuration
        self._lock = RLock()
        self._loggers: dict[str, ApplicationLogger] = {}

    @property
    def configuration(self) -> LoggingConfiguration:
        return self._configuration

    @property
    def logger_count(self) -> int:
        with self._lock:
            return len(self._loggers)

    def get_logger(self, name: str) -> ApplicationLogger:
        """Return a cached logger for the supplied name."""

        if not isinstance(name, str) or not name.strip():
            raise ValueError("logger name must be a non-empty string")

        name = name.strip()

        with self._lock:
            if name in self._loggers:
                return self._loggers[name]

            logger = logging.getLogger(name)
            logger.setLevel(self._configuration.level.value)
            logger.propagate = False

            if not logger.handlers:
                self._configure_handlers(logger)

            application_logger = ApplicationLogger(logger)
            self._loggers[name] = application_logger

            return application_logger

    def _configure_handlers(self, logger: logging.Logger) -> None:
        formatter = logging.Formatter(
            fmt=self._configuration.log_format,
            datefmt=self._configuration.date_format,
        )

        if self._configuration.console_enabled:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(self._configuration.level.value)
            logger.addHandler(console_handler)

        if self._configuration.file_enabled:
            assert self._configuration.file_path is not None

            self._configuration.file_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            file_handler = logging.FileHandler(
                self._configuration.file_path,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(self._configuration.level.value)
            logger.addHandler(file_handler)
