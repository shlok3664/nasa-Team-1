"""Failure information produced during query dispatch."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class QueryDispatchFailure:
    """Describes why a query could not be executed successfully."""

    query_id: UUID
    query_type: str
    exception: Exception

    def __post_init__(self) -> None:
        if not isinstance(self.query_id, UUID):
            raise TypeError("query_id must be a UUID")

        if not isinstance(self.query_type, str):
            raise TypeError("query_type must be a string")

        if not self.query_type.strip():
            raise ValueError("query_type cannot be empty")

        if not isinstance(self.exception, Exception):
            raise TypeError("exception must be an Exception")
