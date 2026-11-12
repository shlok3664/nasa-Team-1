"""Query handler contract."""

from typing import Protocol, TypeVar

from earth_twin_engine.application.queries.application_query import (
    ApplicationQuery,
)

QueryT = TypeVar("QueryT", bound=ApplicationQuery)
ResultT = TypeVar("ResultT")


class QueryHandler(Protocol[QueryT, ResultT]):
    """Contract implemented by objects that handle application queries."""

    def handle(self, query: QueryT) -> ResultT:
        """Retrieve information for a query without changing application state."""
        ...
