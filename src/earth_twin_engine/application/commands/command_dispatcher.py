"""Thread-safe application command registration and dispatch."""

from threading import RLock
from typing import Any

from earth_twin_engine.application.commands.application_command import (
    ApplicationCommand,
)
from earth_twin_engine.application.commands.command_dispatch_failure import (
    CommandDispatchFailure,
)
from earth_twin_engine.application.commands.command_execution_result import (
    CommandExecutionResult,
)
from earth_twin_engine.application.commands.command_handler import CommandHandler


class CommandDispatcher:
    """Registers command handlers and routes commands to their handlers."""

    def __init__(self) -> None:
        self._handlers: dict[type[ApplicationCommand], CommandHandler[Any, Any]] = {}
        self._lock = RLock()

    @property
    def handler_count(self) -> int:
        """Number of registered command handlers."""
        with self._lock:
            return len(self._handlers)

    def register(
        self,
        command_type: type[ApplicationCommand],
        handler: CommandHandler[Any, Any],
    ) -> None:
        """Register one handler for a command type."""

        if not isinstance(command_type, type) or not issubclass(command_type, ApplicationCommand):
            raise TypeError("command_type must be an ApplicationCommand subclass")

        if not callable(getattr(handler, "handle", None)):
            raise TypeError("handler must provide a callable handle method")

        with self._lock:
            if command_type in self._handlers:
                raise ValueError(f"a handler is already registered for {command_type.__name__}")

            self._handlers[command_type] = handler

    def unregister(self, command_type: type[ApplicationCommand]) -> bool:
        """Remove a registered handler. Return whether one was removed."""

        if not isinstance(command_type, type) or not issubclass(command_type, ApplicationCommand):
            raise TypeError("command_type must be an ApplicationCommand subclass")

        with self._lock:
            return self._handlers.pop(command_type, None) is not None

    def is_registered(self, command_type: type[ApplicationCommand]) -> bool:
        """Check whether a command type has a registered handler."""

        if not isinstance(command_type, type) or not issubclass(command_type, ApplicationCommand):
            raise TypeError("command_type must be an ApplicationCommand subclass")

        with self._lock:
            return command_type in self._handlers

    def dispatch(self, command: ApplicationCommand) -> CommandExecutionResult:
        """Execute a command and capture its result or failure."""

        if not isinstance(command, ApplicationCommand):
            raise TypeError("command must be an ApplicationCommand")

        with self._lock:
            handler = self._handlers.get(type(command))

        if handler is None:
            exception = LookupError(f"no handler registered for {type(command).__name__}")
            return CommandExecutionResult(
                command=command,
                failure=CommandDispatchFailure(
                    command_id=command.command_id,
                    command_type=type(command).__name__,
                    exception=exception,
                ),
            )

        try:
            value = handler.handle(command)
        except Exception as exception:
            return CommandExecutionResult(
                command=command,
                failure=CommandDispatchFailure(
                    command_id=command.command_id,
                    command_type=type(command).__name__,
                    exception=exception,
                ),
            )

        return CommandExecutionResult(
            command=command,
            value=value,
        )
