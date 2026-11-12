"""Supported temporal resolutions for Earth science data."""

from enum import StrEnum


class TemporalResolution(StrEnum):
    """Describes the temporal frequency of scientific observations."""

    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
    ANNUAL = "annual"
    IRREGULAR = "irregular"
