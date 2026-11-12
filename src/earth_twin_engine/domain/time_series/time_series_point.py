"""Individual scientific time-series observation."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite


@dataclass(frozen=True, slots=True)
class TimeSeriesPoint:
    """Represents one observation at a specific timestamp.

    A value of None represents a missing observation.
    It is deliberately not interpreted as zero.
    """

    timestamp: datetime
    value: float | None

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, datetime):
            raise TypeError("timestamp must be a datetime")

        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")

        if self.value is not None:
            if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
                raise TypeError("value must be numeric or None")

            if not isfinite(self.value):
                raise ValueError("value must be finite")
