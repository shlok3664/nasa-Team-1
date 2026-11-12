"""Shared fixtures for Data Source Manager tests."""

from datetime import UTC, datetime

import pytest

from earth_twin_engine.domain.datasets.data_provenance import DataProvenance
from earth_twin_engine.domain.datasets.data_request import DataRequest
from earth_twin_engine.domain.datasets.data_source import DataSource
from earth_twin_engine.domain.datasets.dataset import Dataset
from earth_twin_engine.domain.datasets.dataset_metadata import DatasetMetadata
from earth_twin_engine.domain.geography.geographic_region import GeographicRegion
from earth_twin_engine.domain.geography.spatial_boundary import SpatialBoundary
from earth_twin_engine.domain.temporal.temporal_range import TemporalRange
from earth_twin_engine.domain.temporal.temporal_resolution import TemporalResolution
from earth_twin_engine.domain.variables.earth_variable import EarthVariable
from earth_twin_engine.domain.variables.variable_category import VariableCategory
from earth_twin_engine.domain.variables.variable_metadata import VariableMetadata


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
def modis_source() -> DataSource:
    return DataSource(
        source_id="nasa_modis",
        name="MODIS",
        provider="NASA",
    )


@pytest.fixture
def data_request() -> DataRequest:
    variable = EarthVariable(
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
    region = GeographicRegion(
        region_id="india",
        name="India",
        boundary=SpatialBoundary(
            south_latitude=6,
            north_latitude=37,
            west_longitude=68,
            east_longitude=98,
        ),
    )
    temporal_range = TemporalRange(
        start=datetime(2020, 1, 1, tzinfo=UTC),
        end=datetime(2021, 1, 1, tzinfo=UTC),
    )
    return DataRequest(
        variable=variable,
        region=region,
        temporal_range=temporal_range,
        temporal_resolution=TemporalResolution.DAILY,
    )


@pytest.fixture
def dataset(data_request: DataRequest, merra2_source: DataSource) -> Dataset:
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
