"""Result of executing an application command."""

from dataclasses import dataclass
from typing import Any

from earth_twin_engine.application.commands.application_command import (
    ApplicationCommand,
)
from earth_twin_engine.application.commands.command_dispatch_failure import (
    CommandDispatchFailure,
)


@dataclass(frozen=True, slots=True)
class CommandExecutionResult:
    """Contains either a command's returned value or its dispatch failure."""

    command: ApplicationCommand
    value: Any = None
    failure: CommandDispatchFailure | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.command, ApplicationCommand):
            raise TypeError("command must be an ApplicationCommand")

        if self.failure is not None:
            if not isinstance(self.failure, CommandDispatchFailure):
                raise TypeError("failure must be a CommandDispatchFailure or None")

            if self.failure.command_id != self.command.command_id:
                raise ValueError("failure command_id must match the command")

    @property
    def succeeded(self) -> bool:
        """Whether command execution completed without a failure."""
        return self.failure is None

    @property
    def failed(self) -> bool:
        """Whether command execution failed."""
        return self.failure is not None
