"""Commands for statistical testing."""

from dataclasses import dataclass

from earth_twin_engine.application.commands.application_command import (
    ApplicationCommand,
)

from .statistical_test_method import StatisticalTestMethod


@dataclass(frozen=True, slots=True, kw_only=True)
class RunStatisticalTestCommand(ApplicationCommand):
    """Request execution of a statistical test."""

    method: StatisticalTestMethod
    series_ids: tuple[str, ...]
    significance_level: float = 0.05
    reference_value: float | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.method, StatisticalTestMethod):
            raise TypeError("method must be a StatisticalTestMethod.")

        if not isinstance(self.series_ids, tuple) or not self.series_ids:
            raise ValueError("series_ids must be a non-empty tuple.")

        if any(not isinstance(value, str) or not value.strip() for value in self.series_ids):
            raise ValueError("Every series ID must be a non-empty string.")

        if len(set(self.series_ids)) != len(self.series_ids):
            raise ValueError("series_ids must not contain duplicates.")

        if (
            not isinstance(self.significance_level, (int, float))
            or isinstance(self.significance_level, bool)
            or not 0.0 < self.significance_level < 1.0
        ):
            raise ValueError("significance_level must be between 0 and 1.")

        if self.reference_value is not None and (
            not isinstance(self.reference_value, (int, float))
            or isinstance(self.reference_value, bool)
        ):
            raise TypeError("reference_value must be numeric or None.")
