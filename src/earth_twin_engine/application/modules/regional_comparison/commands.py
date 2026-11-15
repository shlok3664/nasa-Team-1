"""Commands for regional comparison."""

from dataclasses import dataclass

from earth_twin_engine.application.commands import ApplicationCommand

from .errors import InvalidRegionalComparisonError


@dataclass(frozen=True, slots=True, kw_only=True)
class CompareRegionsCommand(ApplicationCommand):
    """Request a trend comparison across geographic regions."""

    region_ids: tuple[str, ...]
    variable_id: str

    def __post_init__(self) -> None:
        ApplicationCommand.__post_init__(self)

        if not isinstance(self.region_ids, tuple) or len(self.region_ids) < 2:
            raise InvalidRegionalComparisonError("At least two region IDs must be provided.")

        if any(not isinstance(item, str) or not item.strip() for item in self.region_ids):
            raise InvalidRegionalComparisonError("Every region ID must be a non-empty string.")

        if len(set(self.region_ids)) != len(self.region_ids):
            raise InvalidRegionalComparisonError("Region IDs must be unique.")

        if not isinstance(self.variable_id, str) or not self.variable_id.strip():
            raise InvalidRegionalComparisonError("variable_id must be a non-empty string.")
