"""Regional comparison using existing time-series and trend-analysis services."""

from statistics import fmean

from earth_twin_engine.application.modules.region_manager import RegionManager
from earth_twin_engine.application.modules.time_series_management import TimeSeriesManager
from earth_twin_engine.application.modules.trend_analysis import (
    TrendAnalyzer,
    TrendDirection,
)

from .errors import (
    InvalidRegionalComparisonError,
    RegionalComparisonDataError,
    RegionNotFoundForComparisonError,
)
from .regional_comparison_result import (
    RegionalComparisonResult,
    RegionalTrendResult,
)


class RegionalComparisonService:
    """Compares trends across registered geographic regions."""

    def __init__(
        self,
        region_manager: RegionManager,
        time_series_manager: TimeSeriesManager,
        trend_analyzer: TrendAnalyzer,
    ) -> None:
        if not isinstance(region_manager, RegionManager):
            raise TypeError("region_manager must be a RegionManager")

        if not isinstance(time_series_manager, TimeSeriesManager):
            raise TypeError("time_series_manager must be a TimeSeriesManager")

        if not isinstance(trend_analyzer, TrendAnalyzer):
            raise TypeError("trend_analyzer must be a TrendAnalyzer")

        self._region_manager = region_manager
        self._time_series_manager = time_series_manager
        self._trend_analyzer = trend_analyzer

    def compare(
        self,
        region_ids: tuple[str, ...],
        variable_id: str,
    ) -> RegionalComparisonResult:
        """Compare all registered series belonging to the requested regions."""

        if not isinstance(region_ids, tuple) or len(region_ids) < 2:
            raise InvalidRegionalComparisonError(
                "At least two region IDs must be supplied as a tuple."
            )

        if any(not isinstance(item, str) or not item.strip() for item in region_ids):
            raise InvalidRegionalComparisonError("Every region ID must be a non-empty string.")

        if len(set(region_ids)) != len(region_ids):
            raise InvalidRegionalComparisonError("Region IDs must be unique.")

        if not isinstance(variable_id, str) or not variable_id.strip():
            raise InvalidRegionalComparisonError("variable_id must be a non-empty string.")

        regions = []

        for region_id in region_ids:
            try:
                regions.append(self._region_manager.get_region(region_id))
            except Exception as exc:
                from earth_twin_engine.application.modules.region_manager import (
                    RegionNotFoundError,
                )

                if isinstance(exc, RegionNotFoundError):
                    raise RegionNotFoundForComparisonError(str(exc)) from exc
                raise

        all_series = self._time_series_manager.find_by_variable(variable_id)

        if not all_series:
            raise RegionalComparisonDataError(
                f"No time series are registered for variable '{variable_id}'."
            )

        resolutions = {series.temporal_resolution for series in all_series}

        if len(resolutions) != 1:
            raise RegionalComparisonDataError(
                "Time series must use the same temporal resolution for comparison."
            )

        resolution = next(iter(resolutions))
        regional_results = []

        for region in regions:
            matching_series = tuple(
                series for series in all_series if region.boundary.contains(series.location)
            )

            if not matching_series:
                raise RegionalComparisonDataError(
                    f"No '{variable_id}' time series are located inside "
                    f"region '{region.region_id}'."
                )

            analyses = tuple(self._trend_analyzer.analyze(series) for series in matching_series)

            regional_results.append(
                self._summarize_region(region, variable_id, resolution, analyses)
            )

        # Rank by the absolute average Sen's slope. Regions with unavailable
        # slope estimates are placed after regions with valid estimates.
        ranked = sorted(
            regional_results,
            key=lambda item: (
                item.mean_sen_slope_per_day is None,
                -abs(item.mean_sen_slope_per_day or 0.0),
                item.region.region_id,
            ),
        )

        return RegionalComparisonResult(
            variable_id=variable_id,
            temporal_resolution=resolution,
            regions=tuple(regional_results),
            ranking=tuple(item.region.region_id for item in ranked),
        )

    @staticmethod
    def _summarize_region(
        region,
        variable_id,
        resolution,
        analyses,
    ) -> RegionalTrendResult:
        increasing = sum(item.direction is TrendDirection.INCREASING for item in analyses)
        decreasing = sum(item.direction is TrendDirection.DECREASING for item in analyses)
        stable = sum(item.direction is TrendDirection.STABLE for item in analyses)
        insufficient = sum(item.direction is TrendDirection.INSUFFICIENT_DATA for item in analyses)

        if increasing > decreasing and increasing > stable:
            direction = TrendDirection.INCREASING
        elif decreasing > increasing and decreasing > stable:
            direction = TrendDirection.DECREASING
        elif stable >= increasing and stable >= decreasing:
            direction = TrendDirection.STABLE
        else:
            direction = TrendDirection.INSUFFICIENT_DATA

        linear_slopes = [
            item.linear_slope_per_day for item in analyses if item.linear_slope_per_day is not None
        ]
        sen_slopes = [
            item.sen_slope_per_day for item in analyses if item.sen_slope_per_day is not None
        ]
        taus = [item.kendall_tau for item in analyses if item.kendall_tau is not None]

        return RegionalTrendResult(
            region=region,
            variable_id=variable_id,
            temporal_resolution=resolution,
            series_results=tuple(analyses),
            mean_linear_slope_per_day=fmean(linear_slopes) if linear_slopes else None,
            mean_sen_slope_per_day=fmean(sen_slopes) if sen_slopes else None,
            mean_kendall_tau=fmean(taus) if taus else None,
            direction=direction,
            increasing_series_count=increasing,
            decreasing_series_count=decreasing,
            stable_series_count=stable,
            insufficient_series_count=insufficient,
            significant_series_count=sum(
                item.p_value is not None and item.p_value < item.significance_level
                for item in analyses
            ),
            total_observation_count=sum(item.input_observation_count for item in analyses),
            valid_observation_count=sum(item.valid_observation_count for item in analyses),
            missing_observation_count=sum(item.missing_observation_count for item in analyses),
        )
