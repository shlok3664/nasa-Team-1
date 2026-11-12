"""Represents a failure encountered while cleaning up a resource."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResourceCleanupFailure:
    """Records a resource cleanup failure."""

    resource_id: str
    exception: Exception

    def __post_init__(self) -> None:
        if not isinstance(self.resource_id, str) or not self.resource_id.strip():
            raise ValueError("resource_id must be a non-empty string")

        if not isinstance(self.exception, Exception):
            raise TypeError("exception must be an Exception")
