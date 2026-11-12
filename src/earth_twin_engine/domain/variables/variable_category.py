"""Earth system variable categories."""

from enum import StrEnum


class VariableCategory(StrEnum):
    """Classifies variables by their associated Earth system."""

    ATMOSPHERE = "atmosphere"
    OCEAN = "ocean"
    LAND = "land"
    HYDROLOGY = "hydrology"
    CRYOSPHERE = "cryosphere"
    BIOSPHERE = "biosphere"
    OTHER = "other"
