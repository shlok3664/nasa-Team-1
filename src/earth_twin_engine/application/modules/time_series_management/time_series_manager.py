"""Thread-safe registry for scientific time series."""

from threading import RLock

from earth_twin_engine.application.modules.time_series_management.errors import (
    DuplicateTimeSeriesError,
    TimeSeriesNotFoundError,
)
from earth_twin_engine.domain.time_series import TimeSeries


class TimeSeriesManager:
    """Stores and retrieves time series by their unique identifiers."""

    def __init__(self) -> None:
        self._series: dict[str, TimeSeries] = {}
        self._lock = RLock()

    def register(self, series: TimeSeries) -> None:
        """Register a time series."""

        if not isinstance(series, TimeSeries):
            raise TypeError("series must be a TimeSeries")

        with self._lock:
            if series.series_id in self._series:
                raise DuplicateTimeSeriesError(
                    f"Time series '{series.series_id}' is already registered"
                )

            self._series[series.series_id] = series

    def unregister(self, series_id: str) -> bool:
        """Remove a series, returning whether it existed."""

        if not isinstance(series_id, str) or not series_id.strip():
            raise ValueError("series_id must be a non-empty string")

        with self._lock:
            return self._series.pop(series_id, None) is not None

    def get(self, series_id: str) -> TimeSeries:
        """Retrieve a series by identifier."""

        if not isinstance(series_id, str) or not series_id.strip():
            raise ValueError("series_id must be a non-empty string")

        with self._lock:
            try:
                return self._series[series_id]
            except KeyError as exc:
                raise TimeSeriesNotFoundError(f"Time series '{series_id}' was not found") from exc

    def get_all(self) -> tuple[TimeSeries, ...]:
        """Return all registered time series."""

        with self._lock:
            return tuple(self._series.values())

    def find_by_variable(self, variable_id: str) -> tuple[TimeSeries, ...]:
        """Return series associated with a variable identifier."""

        if not isinstance(variable_id, str) or not variable_id.strip():
            raise ValueError("variable_id must be a non-empty string")

        with self._lock:
            return tuple(
                series
                for series in self._series.values()
                if series.variable.variable_id == variable_id
            )

    def contains(self, series_id: str) -> bool:
        """Check whether a series identifier is registered."""

        with self._lock:
            return series_id in self._series

    @property
    def count(self) -> int:
        """Return the number of registered series."""

        with self._lock:
            return len(self._series)
