"""Structured description of a scientific data validation issue."""

from dataclasses import dataclass

from .validation_severity import ValidationSeverity


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Describes an issue discovered during dataset validation."""

    code: str
    message: str
    severity: ValidationSeverity
    series_id: str | None = None
    observation_index: int | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("code", self.code),
            ("message", self.message),
        ):
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string")

            if not value.strip():
                raise ValueError(f"{field_name} cannot be empty")

        if not isinstance(self.severity, ValidationSeverity):
            raise TypeError("severity must be a ValidationSeverity")

        if self.series_id is not None:
            if not isinstance(self.series_id, str) or not self.series_id.strip():
                raise ValueError("series_id must be a non-empty string or None")

        if self.observation_index is not None:
            if isinstance(self.observation_index, bool) or not isinstance(
                self.observation_index, int
            ):
                raise TypeError("observation_index must be an integer or None")

            if self.observation_index < 0:
                raise ValueError("observation_index cannot be negative")
