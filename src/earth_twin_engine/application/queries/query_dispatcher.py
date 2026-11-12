"""Thread-safe application query registration and dispatch."""

from threading import RLock
from typing import Any

from earth_twin_engine.application.queries.application_query import (
    ApplicationQuery,
)
from earth_twin_engine.application.queries.query_dispatch_failure import (
    QueryDispatchFailure,
)
from earth_twin_engine.application.queries.query_execution_result import (
    QueryExecutionResult,
)
from earth_twin_engine.application.queries.query_handler import QueryHandler


class QueryDispatcher:
    """Registers query handlers and routes queries to their handlers."""

    def __init__(self) -> None:
        self._handlers: dict[type[ApplicationQuery], QueryHandler[Any, Any]] = {}
        self._lock = RLock()

    @property
    def handler_count(self) -> int:
        """Number of registered query handlers."""
        with self._lock:
            return len(self._handlers)

    def register(
        self,
        query_type: type[ApplicationQuery],
        handler: QueryHandler[Any, Any],
    ) -> None:
        """Register one handler for a query type."""

        if not isinstance(query_type, type) or not issubclass(query_type, ApplicationQuery):
            raise TypeError("query_type must be an ApplicationQuery subclass")

        if not callable(getattr(handler, "handle", None)):
            raise TypeError("handler must provide a callable handle method")

        with self._lock:
            if query_type in self._handlers:
                raise ValueError(f"a handler is already registered for {query_type.__name__}")

            self._handlers[query_type] = handler

    def unregister(self, query_type: type[ApplicationQuery]) -> bool:
        """Remove a registered handler. Return whether one was removed."""

        if not isinstance(query_type, type) or not issubclass(query_type, ApplicationQuery):
            raise TypeError("query_type must be an ApplicationQuery subclass")

        with self._lock:
            return self._handlers.pop(query_type, None) is not None

    def is_registered(self, query_type: type[ApplicationQuery]) -> bool:
        """Check whether a query type has a registered handler."""

        if not isinstance(query_type, type) or not issubclass(query_type, ApplicationQuery):
            raise TypeError("query_type must be an ApplicationQuery subclass")

        with self._lock:
            return query_type in self._handlers

    def dispatch(self, query: ApplicationQuery) -> QueryExecutionResult:
        """Execute a query and capture its result or failure."""

        if not isinstance(query, ApplicationQuery):
            raise TypeError("query must be an ApplicationQuery")

        with self._lock:
            handler = self._handlers.get(type(query))

        if handler is None:
            exception = LookupError(f"no handler registered for {type(query).__name__}")
            return QueryExecutionResult(
                query=query,
                failure=QueryDispatchFailure(
                    query_id=query.query_id,
                    query_type=type(query).__name__,
                    exception=exception,
                ),
            )

        try:
            value = handler.handle(query)
        except Exception as exception:
            return QueryExecutionResult(
                query=query,
                failure=QueryDispatchFailure(
                    query_id=query.query_id,
                    query_type=type(query).__name__,
                    exception=exception,
                ),
            )

        return QueryExecutionResult(
            query=query,
            value=value,
        )
