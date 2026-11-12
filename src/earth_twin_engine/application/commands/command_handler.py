"""Command handler contract."""

from typing import Protocol, TypeVar

from earth_twin_engine.application.commands.application_command import (
    ApplicationCommand,
)

CommandT = TypeVar("CommandT", bound=ApplicationCommand)
ResultT = TypeVar("ResultT")


class CommandHandler(Protocol[CommandT, ResultT]):
    """Contract implemented by objects that handle application commands."""

    def handle(self, command: CommandT) -> ResultT:
        """Execute a command and return its result."""
        ...
