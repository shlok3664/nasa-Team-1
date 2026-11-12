from uuid import uuid4

import pytest

from earth_twin_engine.application.queries import (
    ApplicationQuery,
    QueryDispatchFailure,
    QueryExecutionResult,
)


def test_successful_execution_result() -> None:
    query = ApplicationQuery()
    result = QueryExecutionResult(query=query, value=42)

    assert result.succeeded is True
    assert result.failed is False
    assert result.value == 42
    assert result.failure is None


def test_failed_execution_result() -> None:
    query = ApplicationQuery()
    failure = QueryDispatchFailure(
        query_id=query.query_id,
        query_type="ApplicationQuery",
        exception=RuntimeError("Execution failed"),
    )
    result = QueryExecutionResult(
        query=query,
        failure=failure,
    )

    assert result.failed is True
    assert result.succeeded is False
    assert result.failure is failure


def test_reject_invalid_query() -> None:
    with pytest.raises(TypeError):
        QueryExecutionResult(query="invalid")  # type: ignore[arg-type]


def test_reject_invalid_failure() -> None:
    with pytest.raises(TypeError):
        QueryExecutionResult(
            query=ApplicationQuery(),
            failure="invalid",  # type: ignore[arg-type]
        )


def test_reject_failure_for_different_query() -> None:
    query = ApplicationQuery()
    failure = QueryDispatchFailure(
        query_id=uuid4(),
        query_type="ApplicationQuery",
        exception=RuntimeError("Execution failed"),
    )

    with pytest.raises(ValueError, match="must match"):
        QueryExecutionResult(
            query=query,
            failure=failure,
        )


def test_reject_invalid_failure_query_id() -> None:
    with pytest.raises(TypeError):
        QueryDispatchFailure(
            query_id="invalid",  # type: ignore[arg-type]
            query_type="ApplicationQuery",
            exception=RuntimeError("Execution failed"),
        )


def test_reject_empty_failure_query_type() -> None:
    with pytest.raises(ValueError):
        QueryDispatchFailure(
            query_id=uuid4(),
            query_type=" ",
            exception=RuntimeError("Execution failed"),
        )


def test_reject_invalid_failure_exception() -> None:
    with pytest.raises(TypeError):
        QueryDispatchFailure(
            query_id=uuid4(),
            query_type="ApplicationQuery",
            exception="invalid",  # type: ignore[arg-type]
        )
