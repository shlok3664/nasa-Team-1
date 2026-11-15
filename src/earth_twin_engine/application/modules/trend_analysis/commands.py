"""Commands for trend analysis."""

from dataclasses import dataclass

from earth_twin_engine.application.commands.application_command import ApplicationCommand


@dataclass(frozen=True, slots=True, kw_only=True)
class AnalyzeTimeSeriesTrendCommand(ApplicationCommand):
    """Request statistical trend analysis for a registered time series."""

    series_id: str

    def __post_init__(self) -> None:
        ApplicationCommand.__post_init__(self)

        if not isinstance(self.series_id, str) or not self.series_id.strip():
            raise ValueError("series_id must be a non-empty string.")
