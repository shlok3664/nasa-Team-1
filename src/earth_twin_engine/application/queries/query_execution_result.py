"""Result of executing an application query."""

from dataclasses import dataclass
from typing import Any

from earth_twin_engine.application.queries.application_query import (
    ApplicationQuery,
)
from earth_twin_engine.application.queries.query_dispatch_failure import (
    QueryDispatchFailure,
)


@dataclass(frozen=True, slots=True)
class QueryExecutionResult:
    """Contains either a query's returned value or its dispatch failure."""

    query: ApplicationQuery
    value: Any = None
    failure: QueryDispatchFailure | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.query, ApplicationQuery):
            raise TypeError("query must be an ApplicationQuery")

        if self.failure is not None:
            if not isinstance(self.failure, QueryDispatchFailure):
                raise TypeError("failure must be a QueryDispatchFailure or None")

            if self.failure.query_id != self.query.query_id:
                raise ValueError("failure query_id must match the query")

    @property
    def succeeded(self) -> bool:
        """Whether query execution completed without a failure."""
        return self.failure is None

    @property
    def failed(self) -> bool:
        """Whether query execution failed."""
        return self.failure is not None
