"""Normalizes exceptions into structured application error reports."""

from earth_twin_engine.application.error_handling.application_error import (
    ApplicationError,
)
from earth_twin_engine.application.error_handling.error_category import (
    ErrorCategory,
)
from earth_twin_engine.application.error_handling.error_context import (
    ErrorContext,
)
from earth_twin_engine.application.error_handling.error_report import ErrorReport
from earth_twin_engine.application.error_handling.error_severity import (
    ErrorSeverity,
)


class ApplicationErrorHandler:
    """Converts application and unexpected exceptions into error reports."""

    def handle(
        self,
        exception: Exception,
        context: ErrorContext | None = None,
    ) -> ErrorReport:
        """Normalize an exception without suppressing or modifying it."""

        if not isinstance(exception, Exception):
            raise TypeError("exception must be an Exception")

        if context is not None and not isinstance(context, ErrorContext):
            raise TypeError("context must be an ErrorContext or None")

        if isinstance(exception, ApplicationError):
            return ErrorReport(
                error_code=exception.code,
                message=str(exception),
                category=exception.category,
                severity=exception.severity,
                context=context or exception.context,
                exception_type=type(exception).__name__,
            )

        return ErrorReport(
            error_code="UNHANDLED_EXCEPTION",
            message=str(exception) or type(exception).__name__,
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.ERROR,
            context=context or ErrorContext(),
            exception_type=type(exception).__name__,
        )
