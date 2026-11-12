"""Query for listing registered geographic regions."""

from dataclasses import dataclass

from earth_twin_engine.application.queries import ApplicationQuery


@dataclass(frozen=True, slots=True, kw_only=True)
class ListGeographicRegionsQuery(ApplicationQuery):
    """Requests all registered geographic regions."""

    def __post_init__(self) -> None:
        super(ListGeographicRegionsQuery, self).__post_init__()
