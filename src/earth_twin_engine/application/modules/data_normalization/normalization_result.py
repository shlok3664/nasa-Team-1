"""Result produced by scientific dataset normalization."""

from dataclasses import dataclass

from earth_twin_engine.domain.datasets import Dataset
from earth_twin_engine.domain.time_series import TimeSeries


@dataclass(frozen=True, slots=True)
class NormalizationResult:
    """Contains a normalized dataset and its normalized time series."""

    dataset: Dataset
    time_series: tuple[TimeSeries, ...]
    transformations: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.dataset, Dataset):
            raise TypeError("dataset must be a Dataset instance.")

        if not isinstance(self.time_series, tuple):
            raise TypeError("time_series must be a tuple.")

        if any(not isinstance(series, TimeSeries) for series in self.time_series):
            raise TypeError("Every time_series item must be a TimeSeries instance.")

        if not isinstance(self.transformations, tuple):
            raise TypeError("transformations must be a tuple.")

        if any(
            not isinstance(transformation, str) or not transformation.strip()
            for transformation in self.transformations
        ):
            raise ValueError("Every transformation must be a non-empty string.")
