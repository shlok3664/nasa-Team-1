"""Supported scientific visualization types."""

from enum import StrEnum


class VisualizationType(StrEnum):
    """Describes the scientific view represented by a visualization."""

    TIME_SERIES = "time_series"
    TREND = "trend"
    REGIONAL_COMPARISON = "regional_comparison"
    MAP = "map"
