"""Temporal aggregation of scientific time series."""

from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from statistics import median

from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import (
    AggregationMetadata,
    TimeSeries,
    TimeSeriesPoint,
)

from .aggregation_method import AggregationMethod

_RESOLUTION_ORDER = {
    TemporalResolution.HOURLY: 0,
    TemporalResolution.DAILY: 1,
    TemporalResolution.MONTHLY: 2,
    TemporalResolution.ANNUAL: 3,
}

_AGGREGATORS: dict[AggregationMethod, Callable[[list[float]], float]] = {
    AggregationMethod.MEAN: lambda values: sum(values) / len(values),
    AggregationMethod.SUM: sum,
    AggregationMethod.MINIMUM: min,
    AggregationMethod.MAXIMUM: max,
    AggregationMethod.MEDIAN: median,
}


class TemporalAggregator:
    """Aggregates observations into larger calendar periods."""

    def aggregate(
        self,
        series: TimeSeries,
        target_resolution: TemporalResolution,
        method: AggregationMethod = AggregationMethod.MEAN,
        applied_at: datetime | None = None,
    ) -> TimeSeries:
        """Aggregate a series into the requested temporal resolution."""

        if not isinstance(series, TimeSeries):
            raise TypeError("series must be a TimeSeries")

        if not isinstance(target_resolution, TemporalResolution):
            raise TypeError("target_resolution must be a TemporalResolution")

        if not isinstance(method, AggregationMethod):
            raise TypeError("method must be an AggregationMethod")

        source_resolution = series.temporal_resolution

        if source_resolution not in _RESOLUTION_ORDER:
            raise ValueError("irregular source resolution cannot be calendar-aggregated")

        if target_resolution not in _RESOLUTION_ORDER:
            raise ValueError("irregular target resolution is not supported")

        if _RESOLUTION_ORDER[target_resolution] <= _RESOLUTION_ORDER[source_resolution]:
            raise ValueError("target resolution must be coarser than source resolution")

        if target_resolution not in series.variable.metadata.temporal_resolutions:
            raise ValueError("target resolution is not supported by the variable metadata")

        if applied_at is None:
            applied_at = datetime.now(UTC)

        if not isinstance(applied_at, datetime):
            raise TypeError("applied_at must be a datetime")

        if applied_at.tzinfo is None or applied_at.utcoffset() is None:
            raise ValueError("applied_at must be timezone-aware")

        buckets: dict[datetime, list[TimeSeriesPoint]] = defaultdict(list)

        for point in series.points:
            bucket_timestamp = self._bucket_start(point.timestamp, target_resolution)
            buckets[bucket_timestamp].append(point)

        aggregated_points: list[TimeSeriesPoint] = []

        for timestamp in sorted(buckets):
            bucket_points = buckets[timestamp]
            values = [point.value for point in bucket_points if point.value is not None]

            value = _AGGREGATORS[method](values) if values else None
            aggregated_points.append(TimeSeriesPoint(timestamp=timestamp, value=value))

        metadata = AggregationMetadata(
            method=method.value,
            source_resolution=source_resolution,
            target_resolution=target_resolution,
            input_observation_count=series.observation_count,
            output_observation_count=len(aggregated_points),
            missing_observation_count=series.missing_observation_count,
            applied_at=applied_at,
        )

        return TimeSeries(
            series_id=f"{series.series_id}_{target_resolution.value}",
            variable=series.variable,
            location=series.location,
            temporal_resolution=target_resolution,
            points=tuple(aggregated_points),
            aggregation_metadata=metadata,
        )

    @staticmethod
    def _bucket_start(
        timestamp: datetime,
        resolution: TemporalResolution,
    ) -> datetime:
        """Return the UTC start of the calendar bucket."""

        timestamp = timestamp.astimezone(UTC)

        if resolution is TemporalResolution.DAILY:
            return datetime(timestamp.year, timestamp.month, timestamp.day, tzinfo=UTC)

        if resolution is TemporalResolution.MONTHLY:
            return datetime(timestamp.year, timestamp.month, 1, tzinfo=UTC)

        if resolution is TemporalResolution.ANNUAL:
            return datetime(timestamp.year, 1, 1, tzinfo=UTC)

        raise ValueError(f"Unsupported target resolution: {resolution}")
