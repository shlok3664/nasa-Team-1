"""Spatial aggregation of compatible time series."""

from datetime import UTC, datetime
from statistics import median

from earth_twin_engine.domain.geography import SpatialCoordinate
from earth_twin_engine.domain.time_series import (
    AggregationMetadata,
    TimeSeries,
    TimeSeriesPoint,
)

from .aggregation_method import AggregationMethod


class SpatialAggregator:
    """Combines observations from multiple locations at matching timestamps."""

    def aggregate(
        self,
        series: tuple[TimeSeries, ...],
        series_id: str,
        method: AggregationMethod = AggregationMethod.MEAN,
        applied_at: datetime | None = None,
    ) -> TimeSeries:
        """Create a spatially aggregated series from compatible inputs."""

        if not isinstance(series, tuple):
            raise TypeError("series must be a tuple")

        if len(series) < 2:
            raise ValueError("spatial aggregation requires at least two time series")

        if not all(isinstance(item, TimeSeries) for item in series):
            raise TypeError("series must contain only TimeSeries values")

        if not isinstance(series_id, str) or not series_id.strip():
            raise ValueError("series_id must be a non-empty string")

        if not isinstance(method, AggregationMethod):
            raise TypeError("method must be an AggregationMethod")

        first = series[0]

        for item in series[1:]:
            if item.variable.variable_id != first.variable.variable_id:
                raise ValueError("all time series must describe the same variable")

            if item.temporal_resolution is not first.temporal_resolution:
                raise ValueError("all time series must have the same temporal resolution")

        if applied_at is None:
            applied_at = datetime.now(UTC)

        if not isinstance(applied_at, datetime):
            raise TypeError("applied_at must be a datetime")

        if applied_at.tzinfo is None or applied_at.utcoffset() is None:
            raise ValueError("applied_at must be timezone-aware")

        observations: dict[datetime, list[float]] = {}
        input_count = 0
        missing_count = 0

        for item in series:
            input_count += item.observation_count

            for point in item.points:
                if point.value is None:
                    missing_count += 1
                    continue

                timestamp = point.timestamp.astimezone(UTC)
                observations.setdefault(timestamp, []).append(point.value)

        if not observations:
            raise ValueError("spatial aggregation requires at least one valid observation")

        aggregated_points: list[TimeSeriesPoint] = []

        for timestamp in sorted(observations):
            values = observations[timestamp]

            if method is AggregationMethod.MEAN:
                value = sum(values) / len(values)
            elif method is AggregationMethod.SUM:
                value = sum(values)
            elif method is AggregationMethod.MINIMUM:
                value = min(values)
            elif method is AggregationMethod.MAXIMUM:
                value = max(values)
            else:
                value = median(values)

            aggregated_points.append(TimeSeriesPoint(timestamp=timestamp, value=value))

        # The representative location is the arithmetic centroid of input locations.
        location = SpatialCoordinate(
            latitude=sum(item.location.latitude for item in series) / len(series),
            longitude=sum(item.location.longitude for item in series) / len(series),
        )

        metadata = AggregationMetadata(
            method=f"spatial_{method.value}",
            source_resolution=first.temporal_resolution,
            target_resolution=first.temporal_resolution,
            input_observation_count=input_count,
            output_observation_count=len(aggregated_points),
            missing_observation_count=missing_count,
            applied_at=applied_at,
        )

        return TimeSeries(
            series_id=series_id,
            variable=first.variable,
            location=location,
            temporal_resolution=first.temporal_resolution,
            points=tuple(aggregated_points),
            aggregation_metadata=metadata,
        )
