"""Service that prepares application outputs for scientific visualization."""

from __future__ import annotations

from earth_twin_engine.application.events import ApplicationEvent
from earth_twin_engine.application.modules.regional_comparison import RegionalComparisonResult
from earth_twin_engine.application.modules.statistical_testing import StatisticalTestResult
from earth_twin_engine.application.modules.trend_analysis import TrendAnalysisCompletedEvent
from earth_twin_engine.application.modules.trend_analysis.trend_analysis_result import (
    TrendAnalysisResult,
)
from earth_twin_engine.domain.time_series import TimeSeries

from .errors import VisualizationDataError
from .visualization_models import (
    RegionalComparisonView,
    TimeSeriesView,
    TrendView,
    VariableExplorerView,
    VisualizationResult,
)


class VisualizationService:
    """Converts analysis results into presentation-ready display objects."""

    def build_variable_explorer(self, variable) -> VariableExplorerView:
        """Create the explorer view for one Earth variable."""

        metadata = variable.metadata
        return VariableExplorerView(
            variable_id=variable.variable_id,
            name=variable.name,
            category=variable.category.value,
            unit=metadata.unit,
            temporal_resolutions=metadata.temporal_resolutions,
            keywords=metadata.keywords,
            source_ids=metadata.source_ids,
            description=variable.description,
        )

    def build_time_series_view(self, series: TimeSeries) -> TimeSeriesView:
        """Prepare a time series for charting and inspection."""

        if not isinstance(series, TimeSeries):
            raise TypeError("series must be a TimeSeries")

        return TimeSeriesView(
            series_id=series.series_id,
            variable_id=series.variable.variable_id,
            temporal_resolution=series.temporal_resolution,
            timestamps=tuple(point.timestamp for point in series.points),
            values=tuple(point.value for point in series.points),
            aggregation_metadata=(
                dict(series.aggregation_metadata.__dict__)
                if series.aggregation_metadata is not None
                else None
            ),
            is_aggregated=series.aggregation_metadata is not None,
        )

    def build_trend_view(
        self,
        result: TrendAnalysisResult,
        statistical_result: StatisticalTestResult | None = None,
    ) -> TrendView:
        """Create a presentation view for a time-series trend result."""

        if not isinstance(result, TrendAnalysisResult):
            raise TypeError("result must be a TrendAnalysisResult")

        direction = result.direction.value
        strength = result.strength.value
        p_value = None
        significance = None
        confidence_interval = None

        if statistical_result is not None:
            p_value = statistical_result.p_value
            significance = statistical_result.significant
            confidence_interval = statistical_result.confidence_interval

        return TrendView(
            series_id=result.series_id,
            direction=direction,
            strength=strength,
            slope=result.sen_slope_per_day,
            significance=significance,
            p_value=p_value,
            confidence_interval=confidence_interval,
        )

    def build_regional_comparison_view(
        self,
        result: RegionalComparisonResult,
    ) -> RegionalComparisonView:
        """Prepare a regional comparison for map and summary displays."""

        if not isinstance(result, RegionalComparisonResult):
            raise TypeError("result must be a RegionalComparisonResult")

        summary = {
            "variable_id": result.variable_id,
            "temporal_resolution": result.temporal_resolution,
            "regions": tuple(item.region.region_id for item in result.regions),
            "ranking": result.ranking,
        }

        return RegionalComparisonView(
            variable_id=result.variable_id,
            temporal_resolution=result.temporal_resolution,
            regions=tuple(item.region.region_id for item in result.regions),
            ranking=result.ranking,
            summary=summary,
        )

    def build_visualization_from_event(self, event: ApplicationEvent) -> VisualizationResult:
        """Convert a completed analysis event into a ready-to-render visualization."""

        event_type = type(event).__name__

        if hasattr(event, "result"):
            payload = event.result

            if hasattr(payload, "series_id") and hasattr(payload, "direction"):
                trend_view = self.build_trend_view(payload, getattr(event, "statistical_result", None))
                return VisualizationResult(
                    kind="trend",
                    variable_id=getattr(payload, "variable_id", "unknown"),
                    temporal_resolution=getattr(payload, "temporal_resolution", None),
                    regions=(),
                    title="Trend analysis",
                    summary="Time-series trend rendered for scientific charting.",
                    trend=trend_view,
                    source_event_type=event_type,
                )

            if hasattr(payload, "variable_id") and hasattr(payload, "regions"):
                comparison_view = self.build_regional_comparison_view(payload)
                return VisualizationResult(
                    kind="regional_comparison",
                    variable_id=payload.variable_id,
                    temporal_resolution=payload.temporal_resolution,
                    regions=tuple(item.region.region_id for item in payload.regions),
                    title="Regional comparison",
                    summary="Regional trend summaries prepared for geographic comparison.",
                    regional_comparison=comparison_view,
                    source_event_type=event_type,
                )

            if hasattr(payload, "method") and hasattr(payload, "p_value"):
                return VisualizationResult(
                    kind="statistical_results",
                    variable_id="unknown",
                    temporal_resolution=None,
                    regions=(),
                    title="Statistical results",
                    summary="Statistical test view prepared for presentation.",
                    statistical_summary={
                        "method": payload.method,
                        "series_ids": payload.series_ids,
                        "significant": payload.significant,
                        "p_value": payload.p_value,
                        "confidence_interval": payload.confidence_interval,
                    },
                    source_event_type=event_type,
                )

        if hasattr(event, "method"):
            return VisualizationResult(
                kind="statistical_results",
                variable_id="unknown",
                temporal_resolution=None,
                regions=(),
                title="Statistical results",
                summary="Statistical test view prepared for presentation.",
                statistical_summary={
                    "method": getattr(event, "method", None),
                    "series_ids": getattr(event, "series_ids", ()),
                    "significant": getattr(event, "significant", None),
                },
                source_event_type=event_type,
            )

        raise VisualizationDataError(f"Unsupported visualization event type: {event_type}")
