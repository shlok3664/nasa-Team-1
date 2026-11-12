from dataclasses import dataclass
from unittest.mock import Mock
from uuid import uuid4

import pytest

from earth_twin_engine.application.queries import (
    ApplicationQuery,
    QueryDispatcher,
)


@dataclass(frozen=True, slots=True)
class GetTemperatureQuery(ApplicationQuery):
    location_id: str = "india"


@dataclass(frozen=True, slots=True)
class GetHumidityQuery(ApplicationQuery):
    location_id: str = "india"


class TemperatureQueryHandler:
    def handle(self, query: GetTemperatureQuery) -> float:
        return 34.5


@pytest.fixture
def dispatcher() -> QueryDispatcher:
    return QueryDispatcher()


def test_register_handler(dispatcher: QueryDispatcher) -> None:
    dispatcher.register(GetTemperatureQuery, TemperatureQueryHandler())

    assert dispatcher.is_registered(GetTemperatureQuery)
    assert dispatcher.handler_count == 1


def test_dispatch_query(dispatcher: QueryDispatcher) -> None:
    dispatcher.register(GetTemperatureQuery, TemperatureQueryHandler())

    query = GetTemperatureQuery(location_id="nagpur")
    result = dispatcher.dispatch(query)

    assert result.succeeded is True
    assert result.failed is False
    assert result.query is query
    assert result.value == 34.5
    assert result.failure is None


def test_dispatch_preserves_correlation_id(
    dispatcher: QueryDispatcher,
) -> None:
    correlation_id = uuid4()
    dispatcher.register(GetTemperatureQuery, TemperatureQueryHandler())

    query = GetTemperatureQuery(correlation_id=correlation_id)
    result = dispatcher.dispatch(query)

    assert result.query.correlation_id == correlation_id


def test_reject_duplicate_handler(dispatcher: QueryDispatcher) -> None:
    dispatcher.register(GetTemperatureQuery, TemperatureQueryHandler())

    with pytest.raises(ValueError, match="already registered"):
        dispatcher.register(GetTemperatureQuery, TemperatureQueryHandler())


def test_reject_invalid_query_type(dispatcher: QueryDispatcher) -> None:
    with pytest.raises(TypeError):
        dispatcher.register(str, TemperatureQueryHandler())  # type: ignore[arg-type]


def test_reject_invalid_handler(dispatcher: QueryDispatcher) -> None:
    with pytest.raises(TypeError, match="handle method"):
        dispatcher.register(GetTemperatureQuery, object())  # type: ignore[arg-type]


def test_dispatch_unregistered_query(dispatcher: QueryDispatcher) -> None:
    query = GetTemperatureQuery()

    result = dispatcher.dispatch(query)

    assert result.failed is True
    assert result.succeeded is False
    assert result.failure is not None
    assert isinstance(result.failure.exception, LookupError)
    assert result.failure.query_id == query.query_id


def test_dispatch_captures_handler_exception(
    dispatcher: QueryDispatcher,
) -> None:
    handler = Mock()
    handler.handle.side_effect = RuntimeError("Query failed")
    dispatcher.register(GetTemperatureQuery, handler)

    query = GetTemperatureQuery()
    result = dispatcher.dispatch(query)

    assert result.failed is True
    assert result.failure is not None
    assert isinstance(result.failure.exception, RuntimeError)
    assert str(result.failure.exception) == "Query failed"


def test_handler_failure_does_not_unregister_handler(
    dispatcher: QueryDispatcher,
) -> None:
    handler = Mock()
    handler.handle.side_effect = RuntimeError("Temporary failure")
    dispatcher.register(GetTemperatureQuery, handler)

    result = dispatcher.dispatch(GetTemperatureQuery())

    assert result.failed is True
    assert dispatcher.is_registered(GetTemperatureQuery)


def test_unregister_handler(dispatcher: QueryDispatcher) -> None:
    dispatcher.register(GetTemperatureQuery, TemperatureQueryHandler())

    assert dispatcher.unregister(GetTemperatureQuery) is True
    assert dispatcher.is_registered(GetTemperatureQuery) is False
    assert dispatcher.handler_count == 0


def test_unregister_missing_handler(dispatcher: QueryDispatcher) -> None:
    assert dispatcher.unregister(GetTemperatureQuery) is False


def test_reject_invalid_unregister_type(dispatcher: QueryDispatcher) -> None:
    with pytest.raises(TypeError):
        dispatcher.unregister(str)  # type: ignore[arg-type]


def test_reject_invalid_registration_check(
    dispatcher: QueryDispatcher,
) -> None:
    with pytest.raises(TypeError):
        dispatcher.is_registered(str)  # type: ignore[arg-type]


def test_dispatch_requires_application_query(
    dispatcher: QueryDispatcher,
) -> None:
    with pytest.raises(TypeError):
        dispatcher.dispatch("invalid")  # type: ignore[arg-type]


def test_handler_for_one_query_type_does_not_handle_another(
    dispatcher: QueryDispatcher,
) -> None:
    dispatcher.register(GetTemperatureQuery, TemperatureQueryHandler())

    result = dispatcher.dispatch(GetHumidityQuery())

    assert result.failed is True
    assert result.failure is not None
    assert isinstance(result.failure.exception, LookupError)


def test_handler_returning_none_is_successful(
    dispatcher: QueryDispatcher,
) -> None:
    handler = Mock()
    handler.handle.return_value = None
    dispatcher.register(GetTemperatureQuery, handler)

    result = dispatcher.dispatch(GetTemperatureQuery())

    assert result.succeeded is True
    assert result.value is None
