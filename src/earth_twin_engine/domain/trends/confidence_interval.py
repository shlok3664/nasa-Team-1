"""Statistical confidence interval value object."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class ConfidenceInterval:
    """Represents a statistical confidence interval."""

    lower_bound: float
    upper_bound: float
    confidence_level: float

    def __post_init__(self) -> None:
        for name, value in (
            ("lower_bound", self.lower_bound),
            ("upper_bound", self.upper_bound),
            ("confidence_level", self.confidence_level),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be numeric")

            if not isfinite(value):
                raise ValueError(f"{name} must be finite")

        if self.lower_bound > self.upper_bound:
            raise ValueError("lower_bound cannot exceed upper_bound")

        if not 0 < self.confidence_level < 1:
            raise ValueError("confidence_level must be between 0 and 1")

    @property
    def width(self) -> float:
        """Return the width of the confidence interval."""

        return self.upper_bound - self.lower_bound

    def contains(self, value: float) -> bool:
        """Check whether a value lies within the interval."""

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("value must be numeric")

        if not isfinite(value):
            raise ValueError("value must be finite")

        return self.lower_bound <= value <= self.upper_bound
