from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from earth_twin_engine.application.queries import ApplicationQuery


def test_create_query() -> None:
    query = ApplicationQuery()

    assert isinstance(query.query_id, UUID)
    assert query.issued_at.tzinfo is UTC
    assert query.correlation_id is None


def test_create_query_with_correlation_id() -> None:
    correlation_id = uuid4()
    query = ApplicationQuery(correlation_id=correlation_id)

    assert query.correlation_id == correlation_id


def test_query_ids_are_unique() -> None:
    first = ApplicationQuery()
    second = ApplicationQuery()

    assert first.query_id != second.query_id


def test_reject_invalid_query_id() -> None:
    with pytest.raises(TypeError):
        ApplicationQuery(query_id="invalid")  # type: ignore[arg-type]


def test_reject_naive_issued_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ApplicationQuery(
            issued_at=datetime(2026, 1, 1),  # type: ignore[arg-type]
        )


def test_reject_invalid_issued_at_type() -> None:
    with pytest.raises(TypeError):
        ApplicationQuery(issued_at="invalid")  # type: ignore[arg-type]


def test_reject_invalid_correlation_id() -> None:
    with pytest.raises(TypeError):
        ApplicationQuery(correlation_id="invalid")  # type: ignore[arg-type]


def test_query_is_immutable() -> None:
    query = ApplicationQuery()

    with pytest.raises(AttributeError):
        query.query_id = uuid4()  # type: ignore[misc]
