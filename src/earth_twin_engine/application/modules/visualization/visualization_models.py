"""Presentation-ready data models for scientific results."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from math import isfinite

from earth_twin_engine.domain.temporal import TemporalResolution


@dataclass(frozen=True, slots=True)
class VariableExplorerView:
    """Structured variable metadata for the variable explorer."""

    variable_id: str
    name: str
    category: str
    unit: str
    temporal_resolutions: tuple[TemporalResolution, ...]
    keywords: tuple[str, ...]
    source_ids: tuple[str, ...]
    description: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.variable_id, str) or not self.variable_id.strip():
            raise ValueError("variable_id must be a non-empty string")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValueError("category must be a non-empty string")
        if not isinstance(self.unit, str) or not self.unit.strip():
            raise ValueError("unit must be a non-empty string")
        if not isinstance(self.temporal_resolutions, tuple):
            raise TypeError("temporal_resolutions must be a tuple")
        if not self.temporal_resolutions:
            raise ValueError("temporal_resolutions cannot be empty")
        if not isinstance(self.keywords, tuple):
            raise TypeError("keywords must be a tuple")
        if not isinstance(self.source_ids, tuple):
            raise TypeError("source_ids must be a tuple")


@dataclass(frozen=True, slots=True)
class TimeSeriesView:
    """Time-series data prepared for visualization."""

    series_id: str
    variable_id: str
    temporal_resolution: TemporalResolution
    timestamps: tuple[datetime, ...]
    values: tuple[float | None, ...]
    aggregation_metadata: dict[str, str] | None = None
    is_aggregated: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.series_id, str) or not self.series_id.strip():
            raise ValueError("series_id must be a non-empty string")
        if not isinstance(self.variable_id, str) or not self.variable_id.strip():
            raise ValueError("variable_id must be a non-empty string")
        if not isinstance(self.temporal_resolution, TemporalResolution):
            raise TypeError("temporal_resolution must be a TemporalResolution")
        if not isinstance(self.timestamps, tuple) or not self.timestamps:
            raise ValueError("timestamps must be a non-empty tuple")
        if not isinstance(self.values, tuple) or len(self.values) != len(self.timestamps):
            raise ValueError("values must match the timestamps length")
        for value in self.values:
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError("time-series values must be numeric or None")
            if not isfinite(float(value)):
                raise ValueError("time-series values must be finite")
        if self.aggregation_metadata is not None and not isinstance(
            self.aggregation_metadata,
            dict,
        ):
            raise TypeError("aggregation_metadata must be a dict or None")


@dataclass(frozen=True, slots=True)
class TrendView:
    """Trend information prepared for display."""

    series_id: str
    direction: str
    strength: str
    slope: float | None = None
    significance: bool | None = None
    p_value: float | None = None
    confidence_interval: tuple[float, float] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.series_id, str) or not self.series_id.strip():
            raise ValueError("series_id must be a non-empty string")
        if not isinstance(self.direction, str) or not self.direction.strip():
            raise ValueError("direction must be a non-empty string")
        if not isinstance(self.strength, str) or not self.strength.strip():
            raise ValueError("strength must be a non-empty string")
        if self.slope is not None and (
            isinstance(self.slope, bool)
            or not isinstance(self.slope, (int, float))
            or not isfinite(float(self.slope))
        ):
            raise ValueError("slope must be finite or None")
        if self.p_value is not None and (
            isinstance(self.p_value, bool)
            or not isinstance(self.p_value, (int, float))
            or not isfinite(float(self.p_value))
            or not 0.0 <= float(self.p_value) <= 1.0
        ):
            raise ValueError("p_value must be between 0 and 1 or None")
        if self.confidence_interval is not None:
            if not isinstance(self.confidence_interval, tuple) or len(self.confidence_interval) != 2:
                raise ValueError("confidence_interval must contain two values")
            lower, upper = self.confidence_interval
            if not isfinite(float(lower)) or not isfinite(float(upper)) or lower > upper:
                raise ValueError("confidence_interval bounds must be ordered and finite")


@dataclass(frozen=True, slots=True)
class RegionalComparisonView:
    """Regional comparison summary prepared for map or chart rendering."""

    variable_id: str
    temporal_resolution: TemporalResolution
    regions: tuple[str, ...]
    ranking: tuple[str, ...]
    summary: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.variable_id, str) or not self.variable_id.strip():
            raise ValueError("variable_id must be a non-empty string")
        if not isinstance(self.temporal_resolution, TemporalResolution):
            raise TypeError("temporal_resolution must be a TemporalResolution")
        if not isinstance(self.regions, tuple) or not self.regions:
            raise ValueError("regions must be a non-empty tuple")
        if not isinstance(self.ranking, tuple) or not self.ranking:
            raise ValueError("ranking must be a non-empty tuple")
        if not isinstance(self.summary, dict):
            raise TypeError("summary must be a dict")


@dataclass(frozen=True, slots=True)
class VisualizationResult:
    """Immutable result object emitted by the visualization module."""

    kind: str
    variable_id: str
    temporal_resolution: TemporalResolution | None
    regions: tuple[str, ...]
    title: str
    summary: str
    explorer: VariableExplorerView | None = None
    time_series: TimeSeriesView | None = None
    trend: TrendView | None = None
    regional_comparison: RegionalComparisonView | None = None
    statistical_summary: dict[str, object] | None = None
    metadata: dict[str, object] = field(default_factory=dict)
    source_event_type: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ValueError("kind must be a non-empty string")
        if not isinstance(self.variable_id, str) or not self.variable_id.strip():
            raise ValueError("variable_id must be a non-empty string")
        if self.temporal_resolution is not None and not isinstance(
            self.temporal_resolution,
            TemporalResolution,
        ):
            raise TypeError("temporal_resolution must be a TemporalResolution or None")
        if not isinstance(self.regions, tuple):
            raise TypeError("regions must be a tuple")
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title must be a non-empty string")
        if not isinstance(self.summary, str) or not self.summary.strip():
            raise ValueError("summary must be a non-empty string")
        if self.explorer is not None and not isinstance(self.explorer, VariableExplorerView):
            raise TypeError("explorer must be a VariableExplorerView or None")
        if self.time_series is not None and not isinstance(self.time_series, TimeSeriesView):
            raise TypeError("time_series must be a TimeSeriesView or None")
        if self.trend is not None and not isinstance(self.trend, TrendView):
            raise TypeError("trend must be a TrendView or None")
        if self.regional_comparison is not None and not isinstance(
            self.regional_comparison,
            RegionalComparisonView,
        ):
            raise TypeError("regional_comparison must be a RegionalComparisonView or None")
        if self.statistical_summary is not None and not isinstance(self.statistical_summary, dict):
            raise TypeError("statistical_summary must be a dict or None")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dict")
