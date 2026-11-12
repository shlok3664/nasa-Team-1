"""Tests for the regional comparison service."""

import pytest

from earth_twin_engine.application.modules.regional_comparison import (
    RegionalComparisonService,
)
from earth_twin_engine.application.modules.regional_comparison.errors import (
    InvalidRegionalComparisonError,
    RegionalComparisonDataError,
    RegionNotFoundForComparisonError,
)
from earth_twin_engine.application.modules.trend_analysis import (
    TrendAnalyzer,
    TrendDirection,
)
from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.variables import (
    EarthVariable,
    VariableCategory,
    VariableMetadata,
)


@pytest.fixture
def service(
    region_manager,
    populated_time_series_manager,
) -> RegionalComparisonService:
    return RegionalComparisonService(
        region_manager=region_manager,
        time_series_manager=populated_time_series_manager,
        trend_analyzer=TrendAnalyzer(),
    )


def test_service_compares_multiple_regions(service) -> None:
    result = service.compare(
        region_ids=("region_north", "region_south"),
        variable_id="surface_temperature",
    )

    assert result.variable_id == "surface_temperature"
    assert result.temporal_resolution is TemporalResolution.DAILY
    assert len(result.regions) == 2
    assert set(result.ranking) == {"region_north", "region_south"}


def test_service_preserves_individual_station_results(service) -> None:
    result = service.compare(
        region_ids=("region_north", "region_south"),
        variable_id="surface_temperature",
    )

    north = next(item for item in result.regions if item.region.region_id == "region_north")
    south = next(item for item in result.regions if item.region.region_id == "region_south")

    assert len(north.series_results) == 1
    assert len(south.series_results) == 1
    assert north.series_results[0].series_id == "north_temperature"
    assert south.series_results[0].series_id == "south_temperature"


def test_service_detects_increasing_and_decreasing_regional_trends(
    service,
) -> None:
    result = service.compare(
        region_ids=("region_north", "region_south"),
        variable_id="surface_temperature",
    )

    north = next(item for item in result.regions if item.region.region_id == "region_north")
    south = next(item for item in result.regions if item.region.region_id == "region_south")

    assert north.direction is TrendDirection.INCREASING
    assert south.direction is TrendDirection.DECREASING
    assert north.mean_sen_slope_per_day == pytest.approx(2.0)
    assert south.mean_sen_slope_per_day == pytest.approx(-2.0)


def test_service_ranks_regions_by_absolute_mean_sen_slope(
    region_manager,
    time_series_manager,
    variable,
    make_series,
) -> None:
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
            [10.0, 13.0, 16.0, 19.0, 22.0, 25.0],
        )
    )

    comparison = RegionalComparisonService(
        region_manager,
        time_series_manager,
        TrendAnalyzer(),
    )

    result = comparison.compare(
        ("region_north", "region_south"),
        "surface_temperature",
    )

    assert result.ranking == ("region_south", "region_north")


def test_service_aggregates_multiple_stations_in_one_region(
    region_manager,
    time_series_manager,
    variable,
    make_series,
) -> None:
    time_series_manager.register(
        make_series(
            variable,
            "north_station_one",
            14.0,
            74.0,
            [10.0, 12.0, 14.0, 16.0, 18.0, 20.0],
        )
    )
    time_series_manager.register(
        make_series(
            variable,
            "north_station_two",
            16.0,
            76.0,
            [20.0, 22.0, 24.0, 26.0, 28.0, 30.0],
        )
    )
    time_series_manager.register(
        make_series(
            variable,
            "south_station",
            -5.0,
            75.0,
            [20.0, 18.0, 16.0, 14.0, 12.0, 10.0],
        )
    )

    service = RegionalComparisonService(
        region_manager,
        time_series_manager,
        TrendAnalyzer(),
    )

    result = service.compare(
        ("region_north", "region_south"),
        "surface_temperature",
    )

    north = next(item for item in result.regions if item.region.region_id == "region_north")

    assert len(north.series_results) == 2
    assert north.increasing_series_count == 2
    assert north.mean_sen_slope_per_day == pytest.approx(2.0)
    assert north.total_observation_count == 12


def test_service_supports_overlapping_geographic_regions(
    make_region,
    region_manager,
    time_series_manager,
    variable,
    make_series,
) -> None:
    region_manager.register(make_region("region_overlap", 12.0, 18.0, 72.0, 78.0))
    time_series_manager.register(
        make_series(
            variable,
            "overlapping_station",
            15.0,
            75.0,
            [10.0, 12.0, 14.0, 16.0, 18.0, 20.0],
        )
    )
    time_series_manager.register(
        make_series(
            variable,
            "south_station",
            -5.0,
            75.0,
            [20.0, 18.0, 16.0, 14.0, 12.0, 10.0],
        )
    )

    service = RegionalComparisonService(
        region_manager,
        time_series_manager,
        TrendAnalyzer(),
    )

    result = service.compare(
        ("region_north", "region_overlap"),
        "surface_temperature",
    )

    north, overlap = result.regions

    assert len(north.series_results) == 1
    assert len(overlap.series_results) == 1
    assert north.series_results[0].series_id == "overlapping_station"
    assert overlap.series_results[0].series_id == "overlapping_station"


def test_service_counts_observations_and_significant_series(service) -> None:
    result = service.compare(
        ("region_north", "region_south"),
        "surface_temperature",
    )

    for regional_result in result.regions:
        assert regional_result.total_observation_count == 6
        assert regional_result.valid_observation_count == 6
        assert regional_result.missing_observation_count == 0
        assert regional_result.significant_series_count == 1


def test_service_preserves_missing_observation_counts(
    region_manager,
    time_series_manager,
    variable,
    make_series,
) -> None:
    time_series_manager.register(
        make_series(
            variable,
            "north_temperature",
            15.0,
            75.0,
            [10.0, None, 14.0, 16.0, None, 20.0],
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

    service = RegionalComparisonService(
        region_manager,
        time_series_manager,
        TrendAnalyzer(),
    )

    result = service.compare(
        ("region_north", "region_south"),
        "surface_temperature",
    )

    north = next(item for item in result.regions if item.region.region_id == "region_north")

    assert north.total_observation_count == 6
    assert north.valid_observation_count == 4
    assert north.missing_observation_count == 2


@pytest.mark.parametrize(
    "region_ids",
    [
        (),
        ("region_north",),
        ("region_north", "region_north"),
        ("region_north", ""),
        ("region_north", 123),
        ["region_north", "region_south"],
    ],
)
def test_service_rejects_invalid_region_ids(
    service,
    region_ids,
) -> None:
    with pytest.raises(InvalidRegionalComparisonError):
        service.compare(region_ids, "surface_temperature")


@pytest.mark.parametrize("variable_id", ["", " ", None, 123])
def test_service_rejects_invalid_variable_id(
    service,
    variable_id,
) -> None:
    with pytest.raises(InvalidRegionalComparisonError):
        service.compare(
            ("region_north", "region_south"),
            variable_id,
        )


def test_service_rejects_unknown_region(service) -> None:
    with pytest.raises(RegionNotFoundForComparisonError):
        service.compare(
            ("region_north", "unknown_region"),
            "surface_temperature",
        )


def test_service_rejects_unknown_variable(
    service,
) -> None:
    with pytest.raises(RegionalComparisonDataError, match="No time series"):
        service.compare(
            ("region_north", "region_south"),
            "unknown_variable",
        )


def test_service_rejects_region_without_matching_series(
    region_manager,
    time_series_manager,
    variable,
    make_series,
) -> None:
    time_series_manager.register(
        make_series(
            variable,
            "north_temperature",
            15.0,
            75.0,
            [10.0, 12.0, 14.0, 16.0, 18.0, 20.0],
        )
    )

    service = RegionalComparisonService(
        region_manager,
        time_series_manager,
        TrendAnalyzer(),
    )

    with pytest.raises(RegionalComparisonDataError, match="No .* time series"):
        service.compare(
            ("region_north", "region_south"),
            "surface_temperature",
        )


def test_service_rejects_incompatible_temporal_resolutions(
    region_manager,
    time_series_manager,
    make_series,
) -> None:
    variable = EarthVariable(
        variable_id="surface_temperature",
        name="Surface Temperature",
        description="Temperature with multiple resolutions.",
        category=next(iter(VariableCategory)),
        metadata=VariableMetadata(
            unit="degC",
            temporal_resolutions=(
                TemporalResolution.DAILY,
                TemporalResolution.MONTHLY,
            ),
        ),
    )

    time_series_manager.register(
        make_series(
            variable,
            "north_temperature",
            15.0,
            75.0,
            [10.0, 12.0, 14.0, 16.0],
            TemporalResolution.DAILY,
        )
    )
    time_series_manager.register(
        make_series(
            variable,
            "south_temperature",
            -5.0,
            75.0,
            [20.0, 18.0, 16.0, 14.0],
            TemporalResolution.MONTHLY,
        )
    )

    service = RegionalComparisonService(
        region_manager,
        time_series_manager,
        TrendAnalyzer(),
    )

    with pytest.raises(RegionalComparisonDataError, match="temporal resolution"):
        service.compare(
            ("region_north", "region_south"),
            "surface_temperature",
        )


def test_service_rejects_invalid_dependencies() -> None:
    with pytest.raises(TypeError, match="RegionManager"):
        RegionalComparisonService(
            "invalid",
            None,
            None,
        )
