"""Application error handling contracts and services."""

from earth_twin_engine.application.error_handling.application_error import (
    ApplicationError,
)
from earth_twin_engine.application.error_handling.application_error_handler import (
    ApplicationErrorHandler,
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

__all__ = [
    "ApplicationError",
    "ApplicationErrorHandler",
    "ErrorCategory",
    "ErrorContext",
    "ErrorReport",
    "ErrorSeverity",
]
