"""Shared fixtures for Data Acquisition tests."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.data_acquisition import (
    DataAcquisitionHandler,
)
from earth_twin_engine.application.modules.data_source_manager import (
    DataSourceManager,
)
from earth_twin_engine.application.modules.region_manager import RegionManager
from earth_twin_engine.application.modules.variable_discovery import VariableCatalog
from earth_twin_engine.domain.datasets import (
    DataProvenance,
    DataRequest,
    Dataset,
    DatasetMetadata,
    DataSource,
)
from earth_twin_engine.domain.geography import GeographicRegion, SpatialBoundary
from earth_twin_engine.domain.temporal import TemporalRange, TemporalResolution
from earth_twin_engine.domain.variables import (
    EarthVariable,
    VariableCategory,
    VariableMetadata,
)


@pytest.fixture
def earth_variable() -> EarthVariable:
    return EarthVariable(
        variable_id="air_temperature",
        name="Air Temperature",
        description="Near-surface atmospheric air temperature.",
        category=VariableCategory.ATMOSPHERE,
        metadata=VariableMetadata(
            unit="K",
            temporal_resolutions=(
                TemporalResolution.HOURLY,
                TemporalResolution.DAILY,
            ),
        ),
    )


@pytest.fixture
def india_region() -> GeographicRegion:
    return GeographicRegion(
        region_id="india",
        name="India",
        description="Geographic boundary covering India.",
        boundary=SpatialBoundary(
            south_latitude=6.0,
            north_latitude=37.0,
            west_longitude=68.0,
            east_longitude=98.0,
        ),
    )


@pytest.fixture
def temporal_range() -> TemporalRange:
    return TemporalRange(
        start=datetime(2020, 1, 1, tzinfo=UTC),
        end=datetime(2021, 1, 1, tzinfo=UTC),
    )


@pytest.fixture
def data_request(
    earth_variable: EarthVariable,
    india_region: GeographicRegion,
    temporal_range: TemporalRange,
) -> DataRequest:
    return DataRequest(
        variable=earth_variable,
        region=india_region,
        temporal_range=temporal_range,
        temporal_resolution=TemporalResolution.DAILY,
    )


@pytest.fixture
def merra2_source() -> DataSource:
    return DataSource(
        source_id="nasa_merra2",
        name="MERRA-2",
        provider="NASA",
        description="NASA atmospheric reanalysis.",
        homepage_url="https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/",
    )


@pytest.fixture
def dataset(
    data_request: DataRequest,
    merra2_source: DataSource,
) -> Dataset:
    return Dataset(
        dataset_id="india_daily_temperature",
        request=data_request,
        metadata=DatasetMetadata(
            title="India Daily Temperature",
            data_format="NetCDF",
        ),
        provenance=DataProvenance(
            source=merra2_source,
            retrieved_at=datetime(2026, 1, 1, tzinfo=UTC),
        ),
    )


@pytest.fixture
def variable_catalog(earth_variable: EarthVariable) -> VariableCatalog:
    return VariableCatalog((earth_variable,))


@pytest.fixture
def region_manager(india_region: GeographicRegion) -> RegionManager:
    manager = RegionManager()
    manager.register(india_region)
    return manager


@pytest.fixture
def data_source_manager(merra2_source: DataSource, dataset: Dataset) -> DataSourceManager:
    manager = DataSourceManager()
    adapter = Mock()
    adapter.source = merra2_source
    adapter.supports.return_value = True
    adapter.is_available.return_value = True
    adapter.retrieve.return_value = dataset
    manager.register(adapter)
    return manager


@pytest.fixture
def event_dispatcher() -> EventDispatcher:
    return EventDispatcher()


@pytest.fixture
def acquisition_handler(
    variable_catalog: VariableCatalog,
    region_manager: RegionManager,
    data_source_manager: DataSourceManager,
    event_dispatcher: EventDispatcher,
) -> DataAcquisitionHandler:
    return DataAcquisitionHandler(
        variable_catalog=variable_catalog,
        region_manager=region_manager,
        data_source_manager=data_source_manager,
        event_dispatcher=event_dispatcher,
    )
