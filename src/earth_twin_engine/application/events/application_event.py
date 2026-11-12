"""Base contract for application events."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ApplicationEvent:
    """Base class for events exchanged between application modules."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: UUID | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, UUID):
            raise TypeError("event_id must be a UUID")

        if not isinstance(self.occurred_at, datetime):
            raise TypeError("occurred_at must be a datetime")

        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None")
