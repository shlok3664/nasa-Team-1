"""Supported scientific aggregation methods."""

from enum import StrEnum


class AggregationMethod(StrEnum):
    """Statistical methods used to aggregate observations."""

    MEAN = "mean"
    SUM = "sum"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    MEDIAN = "median"
