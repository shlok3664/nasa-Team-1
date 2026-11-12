"""Failure information produced during command dispatch."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CommandDispatchFailure:
    """Describes why a command could not be executed successfully."""

    command_id: UUID
    command_type: str
    exception: Exception

    def __post_init__(self) -> None:
        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID")

        if not isinstance(self.command_type, str):
            raise TypeError("command_type must be a string")

        if not self.command_type.strip():
            raise ValueError("command_type cannot be empty")

        if not isinstance(self.exception, Exception):
            raise TypeError("exception must be an Exception")
