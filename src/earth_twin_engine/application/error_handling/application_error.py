"""Base exception type for application-level errors."""

from earth_twin_engine.application.error_handling.error_category import (
    ErrorCategory,
)
from earth_twin_engine.application.error_handling.error_context import (
    ErrorContext,
)
from earth_twin_engine.application.error_handling.error_severity import (
    ErrorSeverity,
)


class ApplicationError(Exception):
    """Represents a structured error raised by the application."""

    def __init__(
        self,
        code: str,
        message: str,
        category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: ErrorContext | None = None,
    ) -> None:
        if not isinstance(code, str) or not code.strip():
            raise ValueError("code must be a non-empty string")

        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must be a non-empty string")

        if not isinstance(category, ErrorCategory):
            raise TypeError("category must be an ErrorCategory")

        if not isinstance(severity, ErrorSeverity):
            raise TypeError("severity must be an ErrorSeverity")

        if context is not None and not isinstance(context, ErrorContext):
            raise TypeError("context must be an ErrorContext or None")

        super().__init__(message)

        self.code = code
        self.category = category
        self.severity = severity
        self.context = context or ErrorContext()
