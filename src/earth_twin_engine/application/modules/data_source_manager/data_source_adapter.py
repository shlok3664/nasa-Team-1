"""Contract implemented by infrastructure-level data source adapters."""

from typing import Protocol, runtime_checkable

from earth_twin_engine.domain.datasets import DataRequest, Dataset, DataSource


@runtime_checkable
class DataSourceAdapter(Protocol):
    """Provides access to one external Earth science data source."""

    @property
    def source(self) -> DataSource: ...

    def supports(self, request: DataRequest) -> bool:
        """Return whether this adapter can fulfil the request."""
        ...

    def is_available(self) -> bool:
        """Check whether the provider can currently be reached."""
        ...

    def retrieve(self, request: DataRequest) -> Dataset:
        """Retrieve and return a validated dataset."""
        ...
