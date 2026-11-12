"""Query for discovering providers compatible with a data request."""

from dataclasses import dataclass

from earth_twin_engine.application.queries import ApplicationQuery
from earth_twin_engine.domain.datasets import DataRequest


@dataclass(frozen=True, slots=True, kw_only=True)
class FindCompatibleDataSourcesQuery(ApplicationQuery):
    request: DataRequest

    def __post_init__(self) -> None:
        super(FindCompatibleDataSourcesQuery, self).__post_init__()

        if not isinstance(self.request, DataRequest):
            raise TypeError("request must be a DataRequest")
