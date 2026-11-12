"""Scientific trend slope value object."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class TrendSlope:
    """Represents the rate of change of a scientific variable."""

    value: float
    unit: str

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise TypeError("value must be numeric")

        if not isfinite(self.value):
            raise ValueError("value must be finite")

        if not isinstance(self.unit, str) or not self.unit.strip():
            raise ValueError("unit must be a non-empty string")
