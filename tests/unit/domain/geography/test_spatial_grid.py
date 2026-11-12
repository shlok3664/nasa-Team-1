"""Tests for regular geographic grids."""

import pytest

from earth_twin_engine.domain.geography import (
    SpatialBoundary,
    SpatialCoordinate,
    SpatialGrid,
)


def create_grid(**overrides: object) -> SpatialGrid:
    boundary = SpatialBoundary(
        south_latitude=0,
        north_latitude=10,
        west_longitude=0,
        east_longitude=20,
    )

    values: dict[str, object] = {
        "boundary": boundary,
        "rows": 10,
        "columns": 20,
    }
    values.update(overrides)

    return SpatialGrid(**values)  # type: ignore[arg-type]


def test_create_valid_grid() -> None:
    grid = create_grid()

    assert grid.rows == 10
    assert grid.columns == 20
    assert grid.cell_count == 200


def test_calculate_grid_resolution() -> None:
    grid = create_grid()

    assert grid.latitude_resolution_degrees == 1.0
    assert grid.longitude_resolution_degrees == 1.0


def test_calculate_first_cell_center() -> None:
    grid = create_grid()

    assert grid.cell_center(0, 0) == SpatialCoordinate(0.5, 0.5)


def test_calculate_last_cell_center() -> None:
    grid = create_grid()

    assert grid.cell_center(9, 19) == SpatialCoordinate(9.5, 19.5)


@pytest.mark.parametrize("rows", [0, -1])
def test_reject_non_positive_rows(rows: int) -> None:
    with pytest.raises(ValueError, match="rows"):
        create_grid(rows=rows)


@pytest.mark.parametrize("columns", [0, -1])
def test_reject_non_positive_columns(columns: int) -> None:
    with pytest.raises(ValueError, match="columns"):
        create_grid(columns=columns)


def test_reject_boolean_dimensions() -> None:
    with pytest.raises(TypeError, match="rows"):
        create_grid(rows=True)


def test_reject_non_integer_dimensions() -> None:
    with pytest.raises(TypeError, match="columns"):
        create_grid(columns=2.5)


def test_reject_invalid_boundary() -> None:
    with pytest.raises(TypeError, match="SpatialBoundary"):
        create_grid(boundary=None)


@pytest.mark.parametrize("row", [-1, 10])
def test_reject_out_of_range_row(row: int) -> None:
    grid = create_grid()

    with pytest.raises(IndexError, match="row"):
        grid.cell_center(row, 0)


@pytest.mark.parametrize("column", [-1, 20])
def test_reject_out_of_range_column(column: int) -> None:
    grid = create_grid()

    with pytest.raises(IndexError, match="column"):
        grid.cell_center(0, column)


def test_reject_non_integer_cell_indices() -> None:
    grid = create_grid()

    with pytest.raises(TypeError, match="row"):
        grid.cell_center(1.5, 0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="column"):
        grid.cell_center(0, True)


def test_antimeridian_grid_cell_centers_wrap_longitude() -> None:
    boundary = SpatialBoundary(
        south_latitude=-10,
        north_latitude=10,
        west_longitude=170,
        east_longitude=-170,
    )

    grid = SpatialGrid(
        boundary=boundary,
        rows=2,
        columns=4,
    )

    assert grid.cell_center(0, 0).longitude == 172.5
    assert grid.cell_center(0, 1).longitude == 177.5
    assert grid.cell_center(0, 2).longitude == -177.5
    assert grid.cell_center(0, 3).longitude == -172.5


def test_grid_is_immutable() -> None:
    grid = create_grid()

    with pytest.raises(AttributeError):
        grid.rows = 5  # type: ignore[misc]
