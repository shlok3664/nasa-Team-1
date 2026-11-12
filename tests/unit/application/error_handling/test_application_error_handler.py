from uuid import uuid4

import pytest

from earth_twin_engine.application.error_handling import (
    ApplicationError,
    ApplicationErrorHandler,
    ErrorCategory,
    ErrorContext,
    ErrorReport,
    ErrorSeverity,
)


@pytest.fixture
def handler() -> ApplicationErrorHandler:
    return ApplicationErrorHandler()


def test_handle_application_error(
    handler: ApplicationErrorHandler,
) -> None:
    context = ErrorContext(
        correlation_id=uuid4(),
        module_id="data_acquisition",
        operation="retrieve_dataset",
    )

    exception = ApplicationError(
        code="DATA_SOURCE_UNAVAILABLE",
        message="The data source is unavailable.",
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.CRITICAL,
        context=context,
    )

    report = handler.handle(exception)

    assert isinstance(report, ErrorReport)
    assert report.error_code == "DATA_SOURCE_UNAVAILABLE"
    assert report.message == str(exception)
    assert report.category is ErrorCategory.NETWORK
    assert report.severity is ErrorSeverity.CRITICAL
    assert report.context is context
    assert report.exception_type == "ApplicationError"
    assert report.report_id is not None
    assert report.occurred_at.tzinfo is not None


def test_handle_unexpected_exception(
    handler: ApplicationErrorHandler,
) -> None:
    exception = ValueError("Invalid input")

    report = handler.handle(exception)

    assert report.error_code == "UNHANDLED_EXCEPTION"
    assert report.message == "Invalid input"
    assert report.category is ErrorCategory.UNKNOWN
    assert report.severity is ErrorSeverity.ERROR
    assert report.exception_type == "ValueError"


def test_handle_exception_with_external_context(
    handler: ApplicationErrorHandler,
) -> None:
    original_context = ErrorContext(module_id="module_a")
    supplied_context = ErrorContext(module_id="module_b")

    exception = ApplicationError(
        code="TEST_ERROR",
        message="Test error",
        context=original_context,
    )

    report = handler.handle(exception, context=supplied_context)

    assert report.context is supplied_context


def test_handle_unexpected_exception_with_context(
    handler: ApplicationErrorHandler,
) -> None:
    context = ErrorContext(
        module_id="data_acquisition",
        operation="retrieve_dataset",
    )

    report = handler.handle(
        RuntimeError("Connection failed"),
        context=context,
    )

    assert report.context is context
    assert report.exception_type == "RuntimeError"


def test_each_report_has_unique_id(
    handler: ApplicationErrorHandler,
) -> None:
    first = handler.handle(ValueError("First"))
    second = handler.handle(ValueError("Second"))

    assert first.report_id != second.report_id


def test_reject_non_exception(
    handler: ApplicationErrorHandler,
) -> None:
    with pytest.raises(TypeError):
        handler.handle("not an exception")  # type: ignore[arg-type]


def test_reject_invalid_context(
    handler: ApplicationErrorHandler,
) -> None:
    with pytest.raises(TypeError):
        handler.handle(
            ValueError("Test"),
            context="invalid",  # type: ignore[arg-type]
        )
