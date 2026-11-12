"""Query for retrieving one registered data source."""

from dataclasses import dataclass

from earth_twin_engine.application.queries import ApplicationQuery


@dataclass(frozen=True, slots=True, kw_only=True)
class GetDataSourceQuery(ApplicationQuery):
    source_id: str

    def __post_init__(self) -> None:
        super(GetDataSourceQuery, self).__post_init__()
        if not isinstance(self.source_id, str):
            raise TypeError("source_id must be a string")
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")
