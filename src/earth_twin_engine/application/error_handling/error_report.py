"""Immutable normalized representation of an application error."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from earth_twin_engine.application.error_handling.error_category import (
    ErrorCategory,
)
from earth_twin_engine.application.error_handling.error_context import (
    ErrorContext,
)
from earth_twin_engine.application.error_handling.error_severity import (
    ErrorSeverity,
)


@dataclass(frozen=True, slots=True)
class ErrorReport:
    """Contains structured information about an encountered error."""

    error_code: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    context: ErrorContext = field(default_factory=ErrorContext)
    exception_type: str = "Exception"
    report_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not isinstance(self.error_code, str) or not self.error_code.strip():
            raise ValueError("error_code must be a non-empty string")

        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be a non-empty string")

        if not isinstance(self.category, ErrorCategory):
            raise TypeError("category must be an ErrorCategory")

        if not isinstance(self.severity, ErrorSeverity):
            raise TypeError("severity must be an ErrorSeverity")

        if not isinstance(self.context, ErrorContext):
            raise TypeError("context must be an ErrorContext")

        if not isinstance(self.exception_type, str) or not self.exception_type.strip():
            raise ValueError("exception_type must be a non-empty string")

        if not isinstance(self.report_id, UUID):
            raise TypeError("report_id must be a UUID")

        if not isinstance(self.occurred_at, datetime):
            raise TypeError("occurred_at must be a datetime")

        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
