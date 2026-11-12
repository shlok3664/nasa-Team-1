"""Application-level logging interface."""

import logging
from collections.abc import Mapping
from typing import Any

from earth_twin_engine.application.logging.log_level import LogLevel


class ApplicationLogger:
    """Provides a consistent logging interface for application modules."""

    def __init__(self, logger: logging.Logger) -> None:
        if not isinstance(logger, logging.Logger):
            raise TypeError("logger must be a logging.Logger")

        self._logger = logger

    @property
    def name(self) -> str:
        return self._logger.name

    @property
    def level(self) -> LogLevel:
        return LogLevel(self._logger.level)

    def is_enabled_for(self, level: LogLevel) -> bool:
        if not isinstance(level, LogLevel):
            raise TypeError("level must be a LogLevel")

        return self._logger.isEnabledFor(level.value)

    def debug(
        self,
        message: str,
        *,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self._log(LogLevel.DEBUG, message, context)

    def info(
        self,
        message: str,
        *,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self._log(LogLevel.INFO, message, context)

    def warning(
        self,
        message: str,
        *,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self._log(LogLevel.WARNING, message, context)

    def error(
        self,
        message: str,
        *,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self._log(LogLevel.ERROR, message, context)

    def critical(
        self,
        message: str,
        *,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self._log(LogLevel.CRITICAL, message, context)

    def exception(
        self,
        message: str,
        *,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self._validate_message(message)
        self._validate_context(context)

        self._logger.exception(
            message,
            extra={"application_context": dict(context or {})},
        )

    def _log(
        self,
        level: LogLevel,
        message: str,
        context: Mapping[str, Any] | None,
    ) -> None:
        self._validate_message(message)
        self._validate_context(context)

        self._logger.log(
            level.value,
            message,
            extra={"application_context": dict(context or {})},
        )

    @staticmethod
    def _validate_message(message: str) -> None:
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must be a non-empty string")

    @staticmethod
    def _validate_context(context: Mapping[str, Any] | None) -> None:
        if context is not None and not isinstance(context, Mapping):
            raise TypeError("context must be a mapping or None")
