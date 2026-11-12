"""Base contract for read-only application queries."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ApplicationQuery:
    """Immutable request for information from the application."""

    query_id: UUID = field(default_factory=uuid4)
    issued_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: UUID | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.query_id, UUID):
            raise TypeError("query_id must be a UUID")

        if not isinstance(self.issued_at, datetime):
            raise TypeError("issued_at must be a datetime")

        if self.issued_at.tzinfo is None or self.issued_at.utcoffset() is None:
            raise ValueError("issued_at must be timezone-aware")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None")
