"""Immutable result of scientific dataset validation."""

from dataclasses import dataclass

from .validation_issue import ValidationIssue
from .validation_severity import ValidationSeverity


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Contains validation findings and observation statistics."""

    dataset_id: str
    issues: tuple[ValidationIssue, ...]
    checked_series_count: int
    observation_count: int
    valid_observation_count: int
    missing_observation_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.dataset_id, str) or not self.dataset_id.strip():
            raise ValueError("dataset_id must be a non-empty string")

        if not isinstance(self.issues, tuple):
            raise TypeError("issues must be a tuple")

        if not all(isinstance(issue, ValidationIssue) for issue in self.issues):
            raise TypeError("issues must contain ValidationIssue values")

        counts = (
            ("checked_series_count", self.checked_series_count),
            ("observation_count", self.observation_count),
            ("valid_observation_count", self.valid_observation_count),
            ("missing_observation_count", self.missing_observation_count),
        )

        for name, value in counts:
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")

            if value < 0:
                raise ValueError(f"{name} cannot be negative")

        if self.valid_observation_count + self.missing_observation_count != (
            self.observation_count
        ):
            raise ValueError("valid and missing observation counts must equal observation_count")

    @property
    def is_valid(self) -> bool:
        """Return whether validation found no errors."""

        return not any(issue.severity is ValidationSeverity.ERROR for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        """Return whether validation found warnings."""

        return any(issue.severity is ValidationSeverity.WARNING for issue in self.issues)

    @property
    def error_count(self) -> int:
        """Return the number of errors."""

        return sum(issue.severity is ValidationSeverity.ERROR for issue in self.issues)

    @property
    def warning_count(self) -> int:
        """Return the number of warnings."""

        return sum(issue.severity is ValidationSeverity.WARNING for issue in self.issues)
