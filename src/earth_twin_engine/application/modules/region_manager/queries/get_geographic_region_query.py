"""Query for retrieving one registered geographic region."""

from dataclasses import dataclass

from earth_twin_engine.application.queries import ApplicationQuery


@dataclass(frozen=True, slots=True, kw_only=True)
class GetGeographicRegionQuery(ApplicationQuery):
    """Requests a geographic region by its identifier."""

    region_id: str

    def __post_init__(self) -> None:
        super(GetGeographicRegionQuery, self).__post_init__()

        if not isinstance(self.region_id, str):
            raise TypeError("region_id must be a string")

        if not self.region_id.strip():
            raise ValueError("region_id must not be empty")
