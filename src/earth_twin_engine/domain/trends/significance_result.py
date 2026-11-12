"""Statistical significance result."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class SignificanceResult:
    """Represents a statistical significance assessment."""

    p_value: float
    alpha: float = 0.05

    def __post_init__(self) -> None:
        for name, value in (
            ("p_value", self.p_value),
            ("alpha", self.alpha),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be numeric")

            if not isfinite(value):
                raise ValueError(f"{name} must be finite")

        if not 0 <= self.p_value <= 1:
            raise ValueError("p_value must be between 0 and 1")

        if not 0 < self.alpha < 1:
            raise ValueError("alpha must be between 0 and 1")

    @property
    def is_significant(self) -> bool:
        """Return whether the p-value is below the significance threshold."""

        return self.p_value < self.alpha
