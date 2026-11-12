"""Tests for scientific visualization state contracts."""

from dataclasses import FrozenInstanceError

import pytest

from earth_twin_engine.domain.visualization import (
    VisualizationState,
    VisualizationType,
)


def create_visualization_state(**overrides: object) -> VisualizationState:
    values: dict[str, object] = {
        "variable": None,
        "temporal_range": None,
        "visualization_type": VisualizationType.TIME_SERIES,
        "regions": (),
    }
    values.update(overrides)
    return VisualizationState(**values)  # type: ignore[arg-type]


def test_create_valid_visualization_state(
    visualization_variable,
    visualization_range,
    visualization_region,
) -> None:
    state = create_visualization_state(
        variable=visualization_variable,
        temporal_range=visualization_range,
        regions=(visualization_region,),
    )

    assert state.variable == visualization_variable
    assert state.temporal_range == visualization_range
    assert state.visualization_type is VisualizationType.TIME_SERIES
    assert state.regions == (visualization_region,)
    assert state.show_trend_line is False
    assert state.show_confidence_interval is False


def test_create_trend_visualization_with_options(
    visualization_variable,
    visualization_range,
    visualization_region,
) -> None:
    state = create_visualization_state(
        variable=visualization_variable,
        temporal_range=visualization_range,
        visualization_type=VisualizationType.TREND,
        regions=(visualization_region,),
        show_trend_line=True,
        show_confidence_interval=True,
    )

    assert state.show_trend_line is True
    assert state.show_confidence_interval is True


def test_create_regional_comparison(
    visualization_variable,
    visualization_range,
    visualization_region,
    second_visualization_region,
) -> None:
    state = create_visualization_state(
        variable=visualization_variable,
        temporal_range=visualization_range,
        visualization_type=VisualizationType.REGIONAL_COMPARISON,
        regions=(visualization_region, second_visualization_region),
    )

    assert len(state.regions) == 2


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("variable", None, "EarthVariable"),
        ("temporal_range", None, "TemporalRange"),
        ("visualization_type", "time_series", "VisualizationType"),
    ],
)
def test_reject_invalid_contract_types(
    visualization_variable,
    visualization_range,
    visualization_region,
    field: str,
    value: object,
    expected_error: str,
) -> None:
    values: dict[str, object] = {
        "variable": visualization_variable,
        "temporal_range": visualization_range,
        "visualization_type": VisualizationType.TIME_SERIES,
        "regions": (visualization_region,),
    }
    values[field] = value

    with pytest.raises(TypeError, match=expected_error):
        create_visualization_state(**values)


def test_reject_non_tuple_regions(
    visualization_variable,
    visualization_range,
    visualization_region,
) -> None:
    with pytest.raises(TypeError, match="tuple"):
        create_visualization_state(
            variable=visualization_variable,
            temporal_range=visualization_range,
            regions=[visualization_region],
        )


def test_reject_empty_regions(
    visualization_variable,
    visualization_range,
) -> None:
    with pytest.raises(ValueError, match="at least one"):
        create_visualization_state(
            variable=visualization_variable,
            temporal_range=visualization_range,
            regions=(),
        )


def test_reject_invalid_region_type(
    visualization_variable,
    visualization_range,
) -> None:
    with pytest.raises(TypeError, match="GeographicRegion"):
        create_visualization_state(
            variable=visualization_variable,
            temporal_range=visualization_range,
            regions=("maharashtra",),
        )


def test_reject_duplicate_regions(
    visualization_variable,
    visualization_range,
    visualization_region,
) -> None:
    with pytest.raises(ValueError, match="duplicates"):
        create_visualization_state(
            variable=visualization_variable,
            temporal_range=visualization_range,
            regions=(visualization_region, visualization_region),
        )


def test_regional_comparison_requires_two_regions(
    visualization_variable,
    visualization_range,
    visualization_region,
) -> None:
    with pytest.raises(ValueError, match="at least two"):
        create_visualization_state(
            variable=visualization_variable,
            temporal_range=visualization_range,
            visualization_type=VisualizationType.REGIONAL_COMPARISON,
            regions=(visualization_region,),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("show_trend_line", 1),
        ("show_confidence_interval", "true"),
    ],
)
def test_reject_non_boolean_options(
    visualization_variable,
    visualization_range,
    visualization_region,
    field: str,
    value: object,
) -> None:
    values: dict[str, object] = {
        "variable": visualization_variable,
        "temporal_range": visualization_range,
        "regions": (visualization_region,),
    }
    values[field] = value

    with pytest.raises(TypeError, match="boolean"):
        create_visualization_state(**values)


def test_visualization_state_is_immutable(
    visualization_variable,
    visualization_range,
    visualization_region,
) -> None:
    state = create_visualization_state(
        variable=visualization_variable,
        temporal_range=visualization_range,
        regions=(visualization_region,),
    )

    with pytest.raises(FrozenInstanceError):
        state.show_trend_line = True  # type: ignore[misc]
