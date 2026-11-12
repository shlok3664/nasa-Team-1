"""Supported statistical test methods."""

from enum import StrEnum


class StatisticalTestMethod(StrEnum):
    """Identifiers for supported statistical tests."""

    MANN_KENDALL = "mann_kendall"
    ONE_SAMPLE_T = "one_sample_t"
    WELCH_T = "welch_t"
