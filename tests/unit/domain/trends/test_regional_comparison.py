"""Tests for regional trend comparisons."""

from datetime import UTC, datetime

import pytest

from earth_twin_engine.domain.geography import (
    GeographicRegion,
    SpatialBoundary,
)
from earth_twin_engine.domain.temporal import TemporalRange
from earth_twin_engine.domain.trends import (
    RegionalComparison,
    RegionalTrend,
    TrendDirection,
    TrendResult,
    TrendSlope,
)


def create_region(region_id: str, name: str) -> GeographicRegion:
    return GeographicRegion(
        region_id=region_id,
        name=name,
        boundary=SpatialBoundary(
            south_latitude=10,
            north_latitude=20,
            west_longitude=70,
            east_longitude=80,
        ),
    )


def create_temporal_range() -> TemporalRange:
    return TemporalRange(
        start=datetime(2010, 1, 1, tzinfo=UTC),
        end=datetime(2020, 1, 1, tzinfo=UTC),
    )


def create_regional_trend(
    variable,
    region: GeographicRegion,
    temporal_range: TemporalRange,
    slope: float,
) -> RegionalTrend:
    result = TrendResult(
        variable=variable,
        region=region,
        temporal_range=temporal_range,
        slope=TrendSlope(slope, "K/year"),
        direction=(
            TrendDirection.INCREASING
            if slope > 0
            else TrendDirection.DECREASING
            if slope < 0
            else TrendDirection.STABLE
        ),
        sample_count=20,
    )

    return RegionalTrend(region=region, result=result)


def test_create_valid_regional_trend(
    trend_variable,
    trend_range,
) -> None:
    region = create_region("maharashtra", "Maharashtra")

    regional_trend = create_regional_trend(
        trend_variable,
        region,
        trend_range,
        0.25,
    )

    assert regional_trend.region.region_id == "maharashtra"
    assert regional_trend.result.slope.value == 0.25


def test_reject_invalid_regional_trend_region(
    trend_variable,
    trend_range,
) -> None:
    region = create_region("maharashtra", "Maharashtra")
    different_region = create_region("gujarat", "Gujarat")

    result = TrendResult(
        variable=trend_variable,
        region=region,
        temporal_range=trend_range,
        slope=TrendSlope(0.25, "K/year"),
        direction=TrendDirection.INCREASING,
        sample_count=20,
    )

    with pytest.raises(ValueError, match="must match"):
        RegionalTrend(region=different_region, result=result)


def test_reject_invalid_regional_trend_contracts() -> None:
    with pytest.raises(TypeError, match="GeographicRegion"):
        RegionalTrend(None, None)  # type: ignore[arg-type]


def test_create_valid_regional_comparison(
    trend_variable,
    trend_range,
) -> None:
    maharashtra = create_region("maharashtra", "Maharashtra")
    gujarat = create_region("gujarat", "Gujarat")

    comparison = RegionalComparison(
        variable=trend_variable,
        temporal_range=trend_range,
        regional_trends=(
            create_regional_trend(trend_variable, maharashtra, trend_range, 0.25),
            create_regional_trend(trend_variable, gujarat, trend_range, -0.10),
        ),
    )

    assert len(comparison.regional_trends) == 2
    assert comparison.regional_trends[0].result.direction is TrendDirection.INCREASING
    assert comparison.regional_trends[1].result.direction is TrendDirection.DECREASING


def test_reject_invalid_comparison_variable(
    trend_range,
) -> None:
    with pytest.raises(TypeError, match="EarthVariable"):
        RegionalComparison(
            variable=None,  # type: ignore[arg-type]
            temporal_range=trend_range,
            regional_trends=(),
        )


def test_reject_invalid_comparison_temporal_range(
    trend_variable,
) -> None:
    with pytest.raises(TypeError, match="TemporalRange"):
        RegionalComparison(
            variable=trend_variable,
            temporal_range=None,  # type: ignore[arg-type]
            regional_trends=(),
        )


def test_reject_mutable_regional_trends(
    trend_variable,
    trend_range,
) -> None:
    with pytest.raises(TypeError, match="tuple"):
        RegionalComparison(
            variable=trend_variable,
            temporal_range=trend_range,
            regional_trends=[],  # type: ignore[arg-type]
        )


def test_reject_comparison_with_fewer_than_two_regions(
    trend_variable,
    trend_range,
) -> None:
    region = create_region("maharashtra", "Maharashtra")
    regional_trend = create_regional_trend(trend_variable, region, trend_range, 0.25)

    with pytest.raises(ValueError, match="at least two"):
        RegionalComparison(
            variable=trend_variable,
            temporal_range=trend_range,
            regional_trends=(regional_trend,),
        )


def test_reject_duplicate_regions(
    trend_variable,
    trend_range,
) -> None:
    region = create_region("maharashtra", "Maharashtra")
    first = create_regional_trend(trend_variable, region, trend_range, 0.25)
    second = create_regional_trend(trend_variable, region, trend_range, 0.30)

    with pytest.raises(ValueError, match="duplicate"):
        RegionalComparison(
            variable=trend_variable,
            temporal_range=trend_range,
            regional_trends=(first, second),
        )


def test_reject_invalid_regional_trend_type(
    trend_variable,
    trend_range,
) -> None:
    with pytest.raises(TypeError, match="RegionalTrend"):
        RegionalComparison(
            variable=trend_variable,
            temporal_range=trend_range,
            regional_trends=("invalid", "also_invalid"),  # type: ignore[arg-type]
        )


def test_reject_different_variables(
    trend_variable,
    trend_range,
) -> None:
    from earth_twin_engine.domain.temporal import TemporalResolution
    from earth_twin_engine.domain.variables import (
        EarthVariable,
        VariableCategory,
        VariableMetadata,
    )

    different_variable = EarthVariable(
        variable_id="precipitation",
        name="Precipitation",
        description="Precipitation amount.",
        category=VariableCategory.ATMOSPHERE,
        metadata=VariableMetadata(
            unit="mm",
            temporal_resolutions=(TemporalResolution.ANNUAL,),
        ),
    )

    first_region = create_region("maharashtra", "Maharashtra")
    second_region = create_region("gujarat", "Gujarat")

    first = create_regional_trend(trend_variable, first_region, trend_range, 0.25)
    second = create_regional_trend(different_variable, second_region, trend_range, 0.10)

    with pytest.raises(ValueError, match="same variable"):
        RegionalComparison(
            variable=trend_variable,
            temporal_range=trend_range,
            regional_trends=(first, second),
        )


def test_reject_different_temporal_ranges(
    trend_variable,
    trend_range,
) -> None:
    another_range = TemporalRange(
        start=datetime(2015, 1, 1, tzinfo=UTC),
        end=datetime(2025, 1, 1, tzinfo=UTC),
    )

    first_region = create_region("maharashtra", "Maharashtra")
    second_region = create_region("gujarat", "Gujarat")

    first = create_regional_trend(trend_variable, first_region, trend_range, 0.25)
    second = create_regional_trend(trend_variable, second_region, another_range, 0.10)

    with pytest.raises(ValueError, match="same temporal range"):
        RegionalComparison(
            variable=trend_variable,
            temporal_range=trend_range,
            regional_trends=(first, second),
        )


def test_regional_comparison_is_immutable(
    trend_variable,
    trend_range,
) -> None:
    first_region = create_region("maharashtra", "Maharashtra")
    second_region = create_region("gujarat", "Gujarat")

    comparison = RegionalComparison(
        variable=trend_variable,
        temporal_range=trend_range,
        regional_trends=(
            create_regional_trend(trend_variable, first_region, trend_range, 0.25),
            create_regional_trend(trend_variable, second_region, trend_range, -0.10),
        ),
    )

    with pytest.raises(AttributeError):
        comparison.regional_trends = ()  # type: ignore[misc]
