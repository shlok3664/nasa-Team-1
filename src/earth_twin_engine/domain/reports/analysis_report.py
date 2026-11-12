"""Scientific analysis report domain contract."""

import re
from dataclasses import dataclass
from datetime import datetime

from earth_twin_engine.domain.temporal import TemporalRange
from earth_twin_engine.domain.trends import TrendResult

_REPORT_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*$")


@dataclass(frozen=True, slots=True)
class AnalysisReport:
    """Immutable record of scientific analysis findings and their context."""

    report_id: str
    title: str
    summary: str
    generated_at: datetime
    temporal_range: TemporalRange
    trend_results: tuple[TrendResult, ...]
    dataset_ids: tuple[str, ...]
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.report_id, str):
            raise TypeError("report_id must be a string")

        if not _REPORT_ID_PATTERN.fullmatch(self.report_id):
            raise ValueError(
                "report_id must start with a lowercase letter and contain "
                "only lowercase letters, numbers, underscores, or hyphens"
            )

        for name, value in (
            ("title", self.title),
            ("summary", self.summary),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        if not isinstance(self.generated_at, datetime):
            raise TypeError("generated_at must be a datetime")

        if self.generated_at.tzinfo is None or self.generated_at.utcoffset() is None:
            raise ValueError("generated_at must be timezone-aware")

        if not isinstance(self.temporal_range, TemporalRange):
            raise TypeError("temporal_range must be a TemporalRange")

        if not isinstance(self.trend_results, tuple):
            raise TypeError("trend_results must be a tuple")

        if not self.trend_results:
            raise ValueError("an analysis report requires at least one trend")

        finding_keys: set[tuple[str, str]] = set()

        for result in self.trend_results:
            if not isinstance(result, TrendResult):
                raise TypeError("trend_results must contain TrendResult values")

            if result.temporal_range != self.temporal_range:
                raise ValueError("all trend results must use the report temporal range")

            finding_key = (
                result.variable.variable_id,
                result.region.region_id,
            )

            if finding_key in finding_keys:
                raise ValueError("report cannot contain duplicate variable-region findings")

            finding_keys.add(finding_key)

        if not isinstance(self.dataset_ids, tuple):
            raise TypeError("dataset_ids must be a tuple")

        if not isinstance(self.limitations, tuple):
            raise TypeError("limitations must be a tuple")

        for name, values in (
            ("dataset_ids", self.dataset_ids),
            ("limitations", self.limitations),
        ):
            if any(not isinstance(value, str) for value in values):
                raise TypeError(f"{name} must contain strings")

            if any(not value.strip() for value in values):
                raise ValueError(f"{name} cannot contain empty strings")

            if len(values) != len(set(values)):
                raise ValueError(f"{name} cannot contain duplicates")
