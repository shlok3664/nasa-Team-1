"""Detection of missing calendar periods in time series."""

from datetime import UTC, datetime

from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import TimeSeries


class MissingPeriodDetector:
    """Identifies absent calendar periods without modifying source observations."""

    def detect(self, series: TimeSeries) -> tuple[datetime, ...]:
        """Return expected period timestamps that are absent from a series."""

        if not isinstance(series, TimeSeries):
            raise TypeError("series must be a TimeSeries")

        resolution = series.temporal_resolution

        if resolution not in (
            TemporalResolution.HOURLY,
            TemporalResolution.DAILY,
            TemporalResolution.MONTHLY,
            TemporalResolution.ANNUAL,
        ):
            raise ValueError("missing-period detection requires a calendar resolution")

        observed = {self._period_start(point.timestamp, resolution) for point in series.points}

        first = min(observed)
        last = max(observed)
        missing: list[datetime] = []
        current = first

        while current < last:
            current = self._next_period(current, resolution)

            if current < last and current not in observed:
                missing.append(current)

        return tuple(missing)

    @staticmethod
    def _period_start(
        timestamp: datetime,
        resolution: TemporalResolution,
    ) -> datetime:
        timestamp = timestamp.astimezone(UTC)

        if resolution is TemporalResolution.HOURLY:
            return timestamp.replace(minute=0, second=0, microsecond=0)

        if resolution is TemporalResolution.DAILY:
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

        if resolution is TemporalResolution.MONTHLY:
            return datetime(timestamp.year, timestamp.month, 1, tzinfo=UTC)

        return datetime(timestamp.year, 1, 1, tzinfo=UTC)

    @staticmethod
    def _next_period(
        timestamp: datetime,
        resolution: TemporalResolution,
    ) -> datetime:
        if resolution is TemporalResolution.HOURLY:
            from datetime import timedelta

            return timestamp + timedelta(hours=1)

        if resolution is TemporalResolution.DAILY:
            from datetime import timedelta

            return timestamp + timedelta(days=1)

        if resolution is TemporalResolution.MONTHLY:
            if timestamp.month == 12:
                return datetime(timestamp.year + 1, 1, 1, tzinfo=UTC)

            return datetime(timestamp.year, timestamp.month + 1, 1, tzinfo=UTC)

        return datetime(timestamp.year + 1, 1, 1, tzinfo=UTC)
