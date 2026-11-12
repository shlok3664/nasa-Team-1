"""Command requesting scientific dataset normalization."""

from dataclasses import dataclass

from earth_twin_engine.application.commands.application_command import (
    ApplicationCommand,
)
from earth_twin_engine.domain.datasets import Dataset
from earth_twin_engine.domain.time_series import TimeSeries


@dataclass(frozen=True, slots=True, kw_only=True)
class NormalizeDatasetCommand(ApplicationCommand):
    """Requests normalization of a dataset and its time-series observations."""

    dataset: Dataset
    time_series: tuple[TimeSeries, ...]

    def __post_init__(self) -> None:
        super(NormalizeDatasetCommand, self).__post_init__()

        if not isinstance(self.dataset, Dataset):
            raise TypeError("dataset must be a Dataset instance.")

        if not isinstance(self.time_series, tuple):
            raise TypeError("time_series must be a tuple.")

        if any(not isinstance(series, TimeSeries) for series in self.time_series):
            raise TypeError("Every time_series item must be a TimeSeries instance.")
