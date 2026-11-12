"""Temporal range value object."""

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class TemporalRange:
    """Represents a timezone-aware temporal interval.

    The interval uses inclusive start and exclusive end semantics.
    """

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.start, datetime):
            raise TypeError("start must be a datetime instance")

        if not isinstance(self.end, datetime):
            raise TypeError("end must be a datetime instance")

        if self.start.tzinfo is None or self.start.utcoffset() is None:
            raise ValueError("start must be timezone-aware")

        if self.end.tzinfo is None or self.end.utcoffset() is None:
            raise ValueError("end must be timezone-aware")

        normalized_start = self.start.astimezone(UTC)
        normalized_end = self.end.astimezone(UTC)

        if normalized_start >= normalized_end:
            raise ValueError("start must be earlier than end")

    @property
    def duration_seconds(self) -> float:
        """Return the interval duration in seconds."""

        return (self.end - self.start).total_seconds()

    def contains(self, timestamp: datetime) -> bool:
        """Check whether a timestamp belongs to this interval."""

        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")

        normalized = timestamp.astimezone(UTC)

        return self.start.astimezone(UTC) <= normalized < self.end.astimezone(UTC)
