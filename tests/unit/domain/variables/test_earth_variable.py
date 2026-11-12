"""Tests for Earth variable domain entities."""

import pytest

from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.variables import (
    EarthVariable,
    VariableCategory,
    VariableMetadata,
)


def create_variable(**overrides: object) -> EarthVariable:
    metadata = VariableMetadata(
        unit="K",
        temporal_resolutions=(TemporalResolution.DAILY,),
    )

    values: dict[str, object] = {
        "variable_id": "air_temperature",
        "name": "Air Temperature",
        "description": "Near-surface atmospheric air temperature.",
        "category": VariableCategory.ATMOSPHERE,
        "metadata": metadata,
    }

    values.update(overrides)
    return EarthVariable(**values)  # type: ignore[arg-type]


def test_create_valid_earth_variable() -> None:
    variable = create_variable()

    assert variable.variable_id == "air_temperature"
    assert variable.name == "Air Temperature"
    assert variable.category is VariableCategory.ATMOSPHERE


@pytest.mark.parametrize(
    "variable_id",
    ["", "AirTemperature", "air-temperature", "1temperature", "air temperature"],
)
def test_reject_invalid_variable_id(variable_id: str) -> None:
    with pytest.raises(ValueError, match="variable_id"):
        create_variable(variable_id=variable_id)


def test_reject_empty_name() -> None:
    with pytest.raises(ValueError, match="name"):
        create_variable(name=" ")


def test_reject_empty_description() -> None:
    with pytest.raises(ValueError, match="description"):
        create_variable(description="")


def test_reject_invalid_category() -> None:
    with pytest.raises(TypeError, match="VariableCategory"):
        create_variable(category="atmosphere")


def test_reject_invalid_metadata() -> None:
    with pytest.raises(TypeError, match="VariableMetadata"):
        create_variable(metadata=None)


def test_earth_variable_is_immutable() -> None:
    variable = create_variable()

    with pytest.raises(AttributeError):
        variable.name = "Changed"  # type: ignore[misc]
