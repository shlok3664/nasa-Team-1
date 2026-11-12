import pytest

from earth_twin_engine.application.error_handling import (
    ApplicationError,
    ErrorCategory,
    ErrorContext,
    ErrorSeverity,
)


def test_create_application_error() -> None:
    context = ErrorContext(module_id="data_acquisition")

    error = ApplicationError(
        code="DATA_SOURCE_UNAVAILABLE",
        message="The requested data source is unavailable.",
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.ERROR,
        context=context,
    )

    assert str(error) == "The requested data source is unavailable."
    assert error.code == "DATA_SOURCE_UNAVAILABLE"
    assert error.category is ErrorCategory.NETWORK
    assert error.severity is ErrorSeverity.ERROR
    assert error.context is context


def test_application_error_defaults() -> None:
    error = ApplicationError(
        code="INTERNAL_FAILURE",
        message="An internal error occurred.",
    )

    assert error.category is ErrorCategory.INTERNAL
    assert error.severity is ErrorSeverity.ERROR
    assert isinstance(error.context, ErrorContext)


def test_application_error_is_exception() -> None:
    error = ApplicationError(
        code="TEST_ERROR",
        message="Test error",
    )

    assert isinstance(error, Exception)

    with pytest.raises(ApplicationError):
        raise error


@pytest.mark.parametrize("code", ["", " "])
def test_reject_invalid_code(code: str) -> None:
    with pytest.raises(ValueError):
        ApplicationError(code=code, message="Test error")


@pytest.mark.parametrize("message", ["", " "])
def test_reject_invalid_message(message: str) -> None:
    with pytest.raises(ValueError):
        ApplicationError(code="TEST_ERROR", message=message)


def test_reject_invalid_category() -> None:
    with pytest.raises(TypeError):
        ApplicationError(
            code="TEST_ERROR",
            message="Test error",
            category="invalid",  # type: ignore[arg-type]
        )


def test_reject_invalid_severity() -> None:
    with pytest.raises(TypeError):
        ApplicationError(
            code="TEST_ERROR",
            message="Test error",
            severity="high",  # type: ignore[arg-type]
        )


def test_reject_invalid_context() -> None:
    with pytest.raises(TypeError):
        ApplicationError(
            code="TEST_ERROR",
            message="Test error",
            context="invalid",  # type: ignore[arg-type]
        )
