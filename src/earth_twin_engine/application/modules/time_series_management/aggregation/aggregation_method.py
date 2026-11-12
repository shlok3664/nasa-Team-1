"""Supported time-series aggregation methods."""

from enum import StrEnum


class AggregationMethod(StrEnum):
    """Statistical methods available for aggregation."""

    MEAN = "mean"
    SUM = "sum"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    MEDIAN = "median"
