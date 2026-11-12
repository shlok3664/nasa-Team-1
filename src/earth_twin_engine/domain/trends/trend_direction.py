"""Direction of an observed scientific trend."""

from enum import StrEnum


class TrendDirection(StrEnum):
    """Describes the direction of a measured trend."""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    UNDETERMINED = "undetermined"
