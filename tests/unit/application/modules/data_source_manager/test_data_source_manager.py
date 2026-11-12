"""Tests for the Data Source Manager."""

from unittest.mock import Mock

import pytest

from earth_twin_engine.application.modules.data_source_manager import (
    AmbiguousDataSourceError,
    DataSourceManager,
    DataSourceNotFoundError,
    DataSourceResponseError,
    DataSourceUnavailableError,
    DuplicateDataSourceError,
    NoCompatibleDataSourceError,
)
from earth_twin_engine.domain.datasets.data_provenance import DataProvenance
from earth_twin_engine.domain.datasets.data_source import DataSource
from earth_twin_engine.domain.datasets.dataset import Dataset
from earth_twin_engine.domain.datasets.dataset_metadata import DatasetMetadata
from earth_twin_engine.domain.temporal import TemporalRange


def make_adapter(source: DataSource, *, compatible: bool = True, available: bool = True):
    adapter = Mock()
    adapter.source = source
    adapter.supports.return_value = compatible
    adapter.is_available.return_value = available
    return adapter


def test_register_and_retrieve_source(merra2_source) -> None:
    manager = DataSourceManager()
    adapter = make_adapter(merra2_source)

    manager.register(adapter)

    assert manager.get_source("nasa_merra2") == merra2_source
    assert manager.get_adapter("nasa_merra2") is adapter
    assert manager.source_count == 1


def test_reject_duplicate_source_id(merra2_source) -> None:
    manager = DataSourceManager()
    manager.register(make_adapter(merra2_source))

    with pytest.raises(DuplicateDataSourceError):
        manager.register(make_adapter(merra2_source))


def test_reject_adapter_with_invalid_source() -> None:
    manager = DataSourceManager()
    adapter = make_adapter("not-a-data-source")

    with pytest.raises(TypeError):
        manager.register(adapter)


def test_reject_adapter_missing_required_methods(merra2_source) -> None:
    manager = DataSourceManager()

    with pytest.raises(TypeError):
        manager.register(type("InvalidAdapter", (), {"source": merra2_source})())


def test_unregister_source(merra2_source) -> None:
    manager = DataSourceManager()
    manager.register(make_adapter(merra2_source))

    assert manager.unregister("nasa_merra2") is True
    assert manager.unregister("nasa_merra2") is False
    assert manager.source_count == 0


def test_get_missing_source_raises(merra2_source) -> None:
    manager = DataSourceManager()

    with pytest.raises(DataSourceNotFoundError):
        manager.get_source("nasa_merra2")


def test_all_sources_are_sorted(merra2_source, modis_source) -> None:
    manager = DataSourceManager()
    manager.register(make_adapter(modis_source))
    manager.register(make_adapter(merra2_source))

    assert manager.all_sources() == (merra2_source, modis_source)


def test_find_compatible_sources(data_request, merra2_source, modis_source) -> None:
    manager = DataSourceManager()
    manager.register(make_adapter(modis_source, compatible=False))
    manager.register(make_adapter(merra2_source, compatible=True))

    assert manager.find_compatible_sources(data_request) == (merra2_source,)


def test_find_compatible_sources_returns_empty_tuple(data_request, merra2_source) -> None:
    manager = DataSourceManager()
    manager.register(make_adapter(merra2_source, compatible=False))

    assert manager.find_compatible_sources(data_request) == ()


def test_resolve_explicit_source(data_request, merra2_source, modis_source) -> None:
    manager = DataSourceManager()
    manager.register(make_adapter(modis_source, compatible=False))
    manager.register(make_adapter(merra2_source))

    request = data_request.__class__(
        variable=data_request.variable,
        region=data_request.region,
        temporal_range=data_request.temporal_range,
        temporal_resolution=data_request.temporal_resolution,
        source_id="nasa_merra2",
    )

    assert manager.resolve_adapter(request).source == merra2_source


def test_explicit_source_must_support_request(data_request, merra2_source) -> None:
    manager = DataSourceManager()
    manager.register(make_adapter(merra2_source, compatible=False))
    request = data_request.__class__(
        variable=data_request.variable,
        region=data_request.region,
        temporal_range=data_request.temporal_range,
        temporal_resolution=data_request.temporal_resolution,
        source_id="nasa_merra2",
    )

    with pytest.raises(NoCompatibleDataSourceError):
        manager.resolve_adapter(request)


def test_ambiguous_source_resolution(data_request, merra2_source, modis_source) -> None:
    manager = DataSourceManager()
    manager.register(make_adapter(merra2_source))
    manager.register(make_adapter(modis_source))

    with pytest.raises(AmbiguousDataSourceError):
        manager.resolve_adapter(data_request)


def test_no_compatible_source(data_request, merra2_source) -> None:
    manager = DataSourceManager()
    manager.register(make_adapter(merra2_source, compatible=False))

    with pytest.raises(NoCompatibleDataSourceError):
        manager.resolve_adapter(data_request)


def test_check_source_availability(merra2_source) -> None:
    manager = DataSourceManager()
    adapter = make_adapter(merra2_source, available=True)
    manager.register(adapter)

    assert manager.is_available("nasa_merra2") is True
    adapter.is_available.assert_called_once()


def test_unavailable_source_is_reported(merra2_source) -> None:
    manager = DataSourceManager()
    manager.register(make_adapter(merra2_source, available=False))

    assert manager.is_available("nasa_merra2") is False


def test_availability_for_missing_source_raises() -> None:
    manager = DataSourceManager()

    with pytest.raises(DataSourceNotFoundError):
        manager.is_available("missing_source")


def test_retrieve_dataset(data_request, dataset, merra2_source) -> None:
    manager = DataSourceManager()
    adapter = make_adapter(merra2_source)
    adapter.retrieve.return_value = dataset
    manager.register(adapter)

    result = manager.retrieve(data_request)

    assert result is dataset
    adapter.retrieve.assert_called_once_with(data_request)


def test_retrieve_rejects_unavailable_source(data_request, merra2_source) -> None:
    manager = DataSourceManager()
    manager.register(make_adapter(merra2_source, available=False))

    with pytest.raises(DataSourceUnavailableError):
        manager.retrieve(data_request)


def test_retrieve_rejects_non_dataset_response(data_request, merra2_source) -> None:
    manager = DataSourceManager()
    adapter = make_adapter(merra2_source)
    adapter.retrieve.return_value = {"unexpected": "payload"}
    manager.register(adapter)

    with pytest.raises(DataSourceResponseError):
        manager.retrieve(data_request)


def test_retrieve_rejects_dataset_for_different_request(
    data_request,
    dataset,
    merra2_source,
) -> None:
    manager = DataSourceManager()
    adapter = make_adapter(merra2_source)
    adapter.retrieve.return_value = dataset
    manager.register(adapter)

    other_request = data_request.__class__(
        variable=data_request.variable,
        region=data_request.region,
        temporal_range=TemporalRange(
            start=data_request.temporal_range.start,
            end=data_request.temporal_range.end.replace(year=2022),
        ),
        temporal_resolution=data_request.temporal_resolution,
    )
    # The returned dataset must correspond to the exact request submitted.
    adapter.retrieve.return_value = dataset

    with pytest.raises(DataSourceResponseError):
        manager.retrieve(other_request)


def test_retrieve_rejects_wrong_provenance_source(
    data_request,
    dataset,
    merra2_source,
    modis_source,
) -> None:
    manager = DataSourceManager()
    adapter = make_adapter(merra2_source)
    adapter.retrieve.return_value = Dataset(
        dataset_id="wrong_source_dataset",
        request=data_request,
        metadata=DatasetMetadata(title="Wrong source"),
        provenance=DataProvenance(
            source=modis_source,
            retrieved_at=dataset.provenance.retrieved_at,
        ),
    )
    manager.register(adapter)

    with pytest.raises(DataSourceResponseError):
        manager.retrieve(data_request)


def test_adapter_supports_must_return_bool(data_request, merra2_source) -> None:
    manager = DataSourceManager()
    adapter = make_adapter(merra2_source)
    adapter.supports.return_value = "yes"
    manager.register(adapter)

    with pytest.raises(TypeError):
        manager.find_compatible_sources(data_request)


def test_adapter_availability_must_return_bool(merra2_source) -> None:
    manager = DataSourceManager()
    adapter = make_adapter(merra2_source)
    adapter.is_available.return_value = 1
    manager.register(adapter)

    with pytest.raises(TypeError):
        manager.is_available("nasa_merra2")
