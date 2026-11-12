"""Events emitted by regional comparison operations."""

from dataclasses import dataclass
from uuid import UUID

from earth_twin_engine.application.events.application_event import ApplicationEvent

from .regional_comparison_result import RegionalComparisonResult


@dataclass(frozen=True, slots=True, kw_only=True)
class RegionalComparisonCompletedEvent(ApplicationEvent):
    """Published when a regional comparison succeeds."""

    command_id: UUID
    correlation_id: UUID | None
    result: RegionalComparisonResult

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None")

        if not isinstance(self.result, RegionalComparisonResult):
            raise TypeError("result must be a RegionalComparisonResult")


@dataclass(frozen=True, slots=True, kw_only=True)
class RegionalComparisonFailedEvent(ApplicationEvent):
    """Published when a regional comparison fails."""

    command_id: UUID
    correlation_id: UUID | None
    variable_id: str
    region_ids: tuple[str, ...]
    error_type: str
    error_message: str

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.command_id, UUID):
            raise TypeError("command_id must be a UUID")

        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None")

        for name, value in (
            ("variable_id", self.variable_id),
            ("error_type", self.error_type),
            ("error_message", self.error_message),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        if not isinstance(self.region_ids, tuple) or not self.region_ids:
            raise ValueError("region_ids must be a non-empty tuple")
