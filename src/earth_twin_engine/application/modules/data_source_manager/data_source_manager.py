"""Coordinates registered Earth science data source adapters."""

from threading import RLock

from earth_twin_engine.domain.datasets import DataRequest, Dataset, DataSource

from .data_source_adapter import DataSourceAdapter
from .data_source_errors import (
    AmbiguousDataSourceError,
    DataSourceNotFoundError,
    DataSourceResponseError,
    DataSourceUnavailableError,
    DuplicateDataSourceError,
    NoCompatibleDataSourceError,
)


class DataSourceManager:
    """Registers providers and routes dataset requests to compatible adapters."""

    def __init__(self) -> None:
        self._adapters: dict[str, DataSourceAdapter] = {}
        self._lock = RLock()

    @property
    def source_count(self) -> int:
        with self._lock:
            return len(self._adapters)

    def register(self, adapter: DataSourceAdapter) -> None:
        """Register an adapter after validating its required interface."""
        if adapter is None:
            raise TypeError("adapter must not be None")

        required_methods = ("supports", "is_available", "retrieve")
        for method_name in required_methods:
            if not callable(getattr(adapter, method_name, None)):
                raise TypeError(f"adapter must implement callable '{method_name}'")

        source = getattr(adapter, "source", None)
        if not isinstance(source, DataSource):
            raise TypeError("adapter.source must be a DataSource")

        with self._lock:
            if source.source_id in self._adapters:
                raise DuplicateDataSourceError(
                    f"Data source '{source.source_id}' is already registered"
                )
            self._adapters[source.source_id] = adapter

    def unregister(self, source_id: str) -> bool:
        """Unregister a provider. Returns False when it was not registered."""
        self._validate_source_id(source_id)
        with self._lock:
            return self._adapters.pop(source_id, None) is not None

    def get_adapter(self, source_id: str) -> DataSourceAdapter:
        """Return a registered adapter by source ID."""
        self._validate_source_id(source_id)
        with self._lock:
            adapter = self._adapters.get(source_id)

        if adapter is None:
            raise DataSourceNotFoundError(f"Data source '{source_id}' is not registered")
        return adapter

    def get_source(self, source_id: str) -> DataSource:
        """Return descriptive metadata for a registered provider."""
        return self.get_adapter(source_id).source

    def all_sources(self) -> tuple[DataSource, ...]:
        """Return registered source metadata in deterministic order."""
        with self._lock:
            sources = tuple(adapter.source for adapter in self._adapters.values())
        return tuple(sorted(sources, key=lambda source: source.source_id))

    def find_compatible_sources(
        self,
        request: DataRequest,
    ) -> tuple[DataSource, ...]:
        """Find all registered providers that support a request."""
        if not isinstance(request, DataRequest):
            raise TypeError("request must be a DataRequest")

        with self._lock:
            adapters = tuple(self._adapters.values())

        compatible: list[DataSource] = []
        for adapter in adapters:
            supported = adapter.supports(request)
            if not isinstance(supported, bool):
                raise TypeError(f"Adapter '{adapter.source.source_id}' supports() must return bool")
            if supported:
                compatible.append(adapter.source)

        return tuple(sorted(compatible, key=lambda source: source.source_id))

    def resolve_adapter(self, request: DataRequest) -> DataSourceAdapter:
        """Resolve exactly one adapter for a request."""
        if not isinstance(request, DataRequest):
            raise TypeError("request must be a DataRequest")

        if request.source_id is not None:
            adapter = self.get_adapter(request.source_id)
            supported = adapter.supports(request)
            if not isinstance(supported, bool):
                raise TypeError(f"Adapter '{request.source_id}' supports() must return bool")
            if not supported:
                raise NoCompatibleDataSourceError(
                    f"Source '{request.source_id}' does not support this request"
                )
            return adapter

        with self._lock:
            adapters = tuple(self._adapters.values())

        compatible: list[DataSourceAdapter] = []
        for adapter in adapters:
            supported = adapter.supports(request)
            if not isinstance(supported, bool):
                raise TypeError(f"Adapter '{adapter.source.source_id}' supports() must return bool")
            if supported:
                compatible.append(adapter)

        if not compatible:
            raise NoCompatibleDataSourceError("No registered data source supports this request")

        if len(compatible) > 1:
            source_ids = ", ".join(sorted(adapter.source.source_id for adapter in compatible))
            raise AmbiguousDataSourceError(
                f"Multiple data sources support this request: {source_ids}"
            )

        return compatible[0]

    def is_available(self, source_id: str) -> bool:
        """Check the current availability of a registered provider."""
        adapter = self.get_adapter(source_id)
        available = adapter.is_available()

        if not isinstance(available, bool):
            raise TypeError(f"Adapter '{source_id}' is_available() must return bool")

        return available

    def retrieve(self, request: DataRequest) -> Dataset:
        """Retrieve a dataset and validate its request and provenance."""
        adapter = self.resolve_adapter(request)
        source = adapter.source

        if not self.is_available(source.source_id):
            raise DataSourceUnavailableError(
                f"Data source '{source.source_id}' is currently unavailable"
            )

        dataset = adapter.retrieve(request)

        if not isinstance(dataset, Dataset):
            raise DataSourceResponseError(f"Adapter '{source.source_id}' did not return a Dataset")

        if dataset.request != request:
            raise DataSourceResponseError(
                f"Adapter '{source.source_id}' returned a dataset for a different request"
            )

        if dataset.provenance.source != source:
            raise DataSourceResponseError(
                f"Dataset provenance does not match source '{source.source_id}'"
            )

        return dataset

    @staticmethod
    def _validate_source_id(source_id: str) -> None:
        if not isinstance(source_id, str):
            raise TypeError("source_id must be a string")
        if not source_id.strip():
            raise ValueError("source_id must not be empty")
