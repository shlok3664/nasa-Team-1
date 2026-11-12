"""Shared fixtures for regional comparison tests."""

from datetime import UTC, datetime, timedelta

import pytest

from earth_twin_engine.application.modules.region_manager import RegionManager
from earth_twin_engine.application.modules.time_series_management import TimeSeriesManager
from earth_twin_engine.domain.geography import (
    GeographicRegion,
    SpatialBoundary,
    SpatialCoordinate,
)
from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import TimeSeries, TimeSeriesPoint
from earth_twin_engine.domain.variables import (
    EarthVariable,
    VariableCategory,
    VariableMetadata,
)


@pytest.fixture
def variable() -> EarthVariable:
    return EarthVariable(
        variable_id="surface_temperature",
        name="Surface Temperature",
        description="Daily surface temperature.",
        category=next(iter(VariableCategory)),
        metadata=VariableMetadata(
            unit="degC",
            temporal_resolutions=(TemporalResolution.DAILY,),
        ),
    )


@pytest.fixture
def make_series():
    def factory(
        variable: EarthVariable,
        series_id: str,
        latitude: float,
        longitude: float,
        values: list[float | None],
        resolution: TemporalResolution = TemporalResolution.DAILY,
    ) -> TimeSeries:
        start = datetime(2025, 1, 1, tzinfo=UTC)
        points = tuple(
            TimeSeriesPoint(
                timestamp=start + timedelta(days=index),
                value=value,
            )
            for index, value in enumerate(values)
        )

        return TimeSeries(
            series_id=series_id,
            variable=variable,
            location=SpatialCoordinate(
                latitude=latitude,
                longitude=longitude,
            ),
            temporal_resolution=resolution,
            points=points,
        )

    return factory


@pytest.fixture
def make_region():
    def factory(
        region_id: str,
        south: float,
        north: float,
        west: float,
        east: float,
    ) -> GeographicRegion:
        return GeographicRegion(
            region_id=region_id,
            name=region_id.replace("_", " ").title(),
            boundary=SpatialBoundary(
                south_latitude=south,
                north_latitude=north,
                west_longitude=west,
                east_longitude=east,
            ),
        )

    return factory


@pytest.fixture
def region_manager(
    make_region,
) -> RegionManager:
    manager = RegionManager()
    manager.register(make_region("region_north", 10.0, 20.0, 70.0, 80.0))
    manager.register(make_region("region_south", -10.0, 0.0, 70.0, 80.0))
    return manager


@pytest.fixture
def time_series_manager() -> TimeSeriesManager:
    return TimeSeriesManager()


@pytest.fixture
def populated_time_series_manager(
    time_series_manager: TimeSeriesManager,
    variable: EarthVariable,
    make_series,
) -> TimeSeriesManager:
    time_series_manager.register(
        make_series(
            variable,
            "north_temperature",
            15.0,
            75.0,
            [10.0, 12.0, 14.0, 16.0, 18.0, 20.0],
        )
    )
    time_series_manager.register(
        make_series(
            variable,
            "south_temperature",
            -5.0,
            75.0,
            [20.0, 18.0, 16.0, 14.0, 12.0, 10.0],
        )
    )
    return time_series_manager


@pytest.fixture
def service(
    region_manager: RegionManager,
    populated_time_series_manager: TimeSeriesManager,
):
    from earth_twin_engine.application.modules.regional_comparison import (
        RegionalComparisonService,
    )
    from earth_twin_engine.application.modules.trend_analysis import TrendAnalyzer

    return RegionalComparisonService(
        region_manager=region_manager,
        time_series_manager=populated_time_series_manager,
        trend_analyzer=TrendAnalyzer(),
    )
