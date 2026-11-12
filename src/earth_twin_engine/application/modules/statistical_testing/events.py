"""Events emitted by statistical testing."""

from dataclasses import dataclass
from uuid import UUID

from earth_twin_engine.application.events.application_event import ApplicationEvent

from .statistical_test_result import StatisticalTestResult


@dataclass(frozen=True, slots=True, kw_only=True)
class StatisticalTestCompletedEvent(ApplicationEvent):
    """Published when a statistical test completes successfully."""

    command_id: UUID
    correlation_id: UUID | None
    result: StatisticalTestResult

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID.")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None.")

        if not isinstance(self.result, StatisticalTestResult):
            raise TypeError("result must be a StatisticalTestResult.")


@dataclass(frozen=True, slots=True, kw_only=True)
class StatisticalTestFailedEvent(ApplicationEvent):
    """Published when a statistical test command fails."""

    command_id: UUID
    correlation_id: UUID | None
    method: str
    series_ids: tuple[str, ...]
    error_type: str
    error_message: str

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID.")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None.")

        if not isinstance(self.method, str) or not self.method.strip():
            raise ValueError("method must be a non-empty string.")

        if not isinstance(self.series_ids, tuple) or not self.series_ids:
            raise ValueError("series_ids must be a non-empty tuple.")

        if not isinstance(self.error_type, str) or not self.error_type.strip():
            raise ValueError("error_type must be a non-empty string.")

        if not isinstance(self.error_message, str):
            raise TypeError("error_message must be a string.")
