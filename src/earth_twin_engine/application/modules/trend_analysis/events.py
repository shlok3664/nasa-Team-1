"""Events emitted by trend analysis."""

from dataclasses import dataclass
from uuid import UUID

from earth_twin_engine.application.events.application_event import ApplicationEvent

from .trend_analysis_result import TrendAnalysisResult


@dataclass(frozen=True, slots=True, kw_only=True)
class TrendAnalysisCompletedEvent(ApplicationEvent):
    """Published after a time-series trend has been analyzed."""

    command_id: UUID
    correlation_id: UUID | None
    result: TrendAnalysisResult

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID.")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None.")

        if not isinstance(self.result, TrendAnalysisResult):
            raise TypeError("result must be a TrendAnalysisResult.")


@dataclass(frozen=True, slots=True, kw_only=True)
class TrendAnalysisFailedEvent(ApplicationEvent):
    """Published when a trend analysis command fails."""

    command_id: UUID
    correlation_id: UUID | None
    series_id: str
    error_type: str
    error_message: str

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID.")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None.")

        if not isinstance(self.series_id, str) or not self.series_id.strip():
            raise ValueError("series_id must be a non-empty string.")

        if not isinstance(self.error_type, str) or not self.error_type.strip():
            raise ValueError("error_type must be a non-empty string.")

        if not isinstance(self.error_message, str):
            raise TypeError("error_message must be a string.")
