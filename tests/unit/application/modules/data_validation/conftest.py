"""Shared fixtures for Data Validation tests."""

from datetime import UTC, datetime

import pytest

from earth_twin_engine.domain.datasets import (
    DataProvenance,
    DataRequest,
    Dataset,
    DatasetMetadata,
    DataSource,
)
from earth_twin_engine.domain.geography import (
    GeographicRegion,
    SpatialBoundary,
    SpatialCoordinate,
)
from earth_twin_engine.domain.temporal import TemporalRange, TemporalResolution
from earth_twin_engine.domain.time_series import TimeSeries, TimeSeriesPoint
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
def data_source() -> DataSource:
    return DataSource(
        source_id="nasa_merra2",
        name="MERRA-2",
        provider="NASA",
        description="NASA atmospheric reanalysis.",
    )


@pytest.fixture
def data_request(earth_variable, india_region, temporal_range) -> DataRequest:
    return DataRequest(
        variable=earth_variable,
        region=india_region,
        temporal_range=temporal_range,
        temporal_resolution=TemporalResolution.DAILY,
    )


@pytest.fixture
def dataset(data_request, data_source) -> Dataset:
    return Dataset(
        dataset_id="india_daily_temperature",
        request=data_request,
        metadata=DatasetMetadata(
            title="India Daily Temperature",
            data_format="NetCDF",
        ),
        provenance=DataProvenance(
            source=data_source,
            retrieved_at=datetime(2026, 1, 1, tzinfo=UTC),
        ),
    )


@pytest.fixture
def valid_time_series(earth_variable) -> TimeSeries:
    return TimeSeries(
        series_id="delhi_temperature",
        variable=earth_variable,
        location=SpatialCoordinate(
            latitude=28.6139,
            longitude=77.2090,
        ),
        temporal_resolution=TemporalResolution.DAILY,
        points=(
            TimeSeriesPoint(
                timestamp=datetime(2020, 1, 1, tzinfo=UTC),
                value=285.4,
            ),
            TimeSeriesPoint(
                timestamp=datetime(2020, 1, 2, tzinfo=UTC),
                value=286.1,
            ),
            TimeSeriesPoint(
                timestamp=datetime(2020, 1, 3, tzinfo=UTC),
                value=284.9,
            ),
        ),
    )


@pytest.fixture
def valid_time_series_collection(valid_time_series) -> tuple[TimeSeries, ...]:
    return (valid_time_series,)
