"""Read-only queries for Earth variable discovery."""

from dataclasses import dataclass

from earth_twin_engine.application.queries.application_query import (
    ApplicationQuery,
)
from earth_twin_engine.domain.temporal.temporal_resolution import (
    TemporalResolution,
)
from earth_twin_engine.domain.variables.variable_category import VariableCategory


@dataclass(frozen=True, slots=True)
class GetEarthVariableQuery(ApplicationQuery):
    """Retrieve one Earth science variable by its identifier."""

    variable_id: str = ""

    def __post_init__(self) -> None:
        super(GetEarthVariableQuery, self).__post_init__()

        if not isinstance(self.variable_id, str):
            raise TypeError("variable_id must be a string")

        if not self.variable_id.strip():
            raise ValueError("variable_id cannot be empty or whitespace")


@dataclass(frozen=True, slots=True)
class DiscoverEarthVariablesQuery(ApplicationQuery):
    """Discover variables using optional scientific metadata filters."""

    category: VariableCategory | None = None
    keyword: str | None = None
    temporal_resolution: TemporalResolution | None = None
    source_id: str | None = None

    def __post_init__(self) -> None:
        super(DiscoverEarthVariablesQuery, self).__post_init__()

        if self.category is not None and not isinstance(self.category, VariableCategory):
            raise TypeError("category must be a VariableCategory or None")

        if self.temporal_resolution is not None and not isinstance(
            self.temporal_resolution, TemporalResolution
        ):
            raise TypeError("temporal_resolution must be a TemporalResolution or None")

        if self.keyword is not None:
            if not isinstance(self.keyword, str):
                raise TypeError("keyword must be a string or None")
            if not self.keyword.strip():
                raise ValueError("keyword cannot be empty or whitespace")

        if self.source_id is not None:
            if not isinstance(self.source_id, str):
                raise TypeError("source_id must be a string or None")
            if not self.source_id.strip():
                raise ValueError("source_id cannot be empty or whitespace")
