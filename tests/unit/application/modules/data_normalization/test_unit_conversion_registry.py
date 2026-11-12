"""Tests for the unit conversion registry."""

import math

import pytest

from earth_twin_engine.application.modules.data_normalization import (
    UnitConversionRegistry,
)
from earth_twin_engine.application.modules.data_normalization.normalization_error import (
    UnsupportedUnitConversionError,
)


def test_registry_converts_celsius_to_kelvin() -> None:
    registry = UnitConversionRegistry()

    assert registry.convert(0, "C", "K") == pytest.approx(273.15)


def test_registry_converts_kelvin_to_celsius() -> None:
    registry = UnitConversionRegistry()

    assert registry.convert(273.15, "K", "C") == pytest.approx(0)


def test_registry_converts_kilometers_per_hour_to_meters_per_second() -> None:
    registry = UnitConversionRegistry()

    assert registry.convert(36, "km/h", "m/s") == pytest.approx(10)


def test_registry_converts_pressure() -> None:
    registry = UnitConversionRegistry()

    assert registry.convert(101325, "Pa", "hPa") == pytest.approx(1013.25)


def test_registry_converts_precipitation() -> None:
    registry = UnitConversionRegistry()

    assert registry.convert(1000, "mm", "m") == pytest.approx(1)


def test_registry_converts_percent_to_fraction() -> None:
    registry = UnitConversionRegistry()

    assert registry.convert(50, "percent", "fraction") == pytest.approx(0.5)


def test_registry_returns_same_value_for_identical_units() -> None:
    registry = UnitConversionRegistry()

    assert registry.convert(12.5, "K", "K") == pytest.approx(12.5)


def test_registry_supports_registered_conversion() -> None:
    registry = UnitConversionRegistry()

    assert registry.supports("C", "K")
    assert registry.supports("K", "K")
    assert not registry.supports("kg", "K")


def test_registry_registers_custom_conversion() -> None:
    registry = UnitConversionRegistry(include_defaults=False)
    registry.register("km", "m", 1000)

    assert registry.convert(2, "km", "m") == pytest.approx(2000)


def test_registry_rejects_duplicate_conversion() -> None:
    registry = UnitConversionRegistry(include_defaults=False)
    registry.register("km", "m", 1000)

    with pytest.raises(ValueError, match="already registered"):
        registry.register("km", "m", 1000)


def test_registry_can_replace_existing_conversion() -> None:
    registry = UnitConversionRegistry(include_defaults=False)
    registry.register("km", "m", 1000)
    registry.register("km", "m", 1001, replace_existing=True)

    assert registry.convert(1, "km", "m") == pytest.approx(1001)


def test_registry_rejects_unsupported_conversion() -> None:
    registry = UnitConversionRegistry(include_defaults=False)

    with pytest.raises(UnsupportedUnitConversionError):
        registry.convert(1, "kg", "K")


@pytest.mark.parametrize("value", [True, "10", None])
def test_registry_rejects_non_numeric_values(value) -> None:
    registry = UnitConversionRegistry()

    with pytest.raises(TypeError):
        registry.convert(value, "K", "K")


@pytest.mark.parametrize("value", [math.inf, -math.inf, math.nan])
def test_registry_rejects_non_finite_values(value) -> None:
    registry = UnitConversionRegistry()

    with pytest.raises(ValueError):
        registry.convert(value, "K", "K")


def test_registry_rejects_invalid_factor() -> None:
    registry = UnitConversionRegistry(include_defaults=False)

    with pytest.raises(ValueError):
        registry.register("a", "b", 0)


def test_registry_rejects_invalid_unit() -> None:
    registry = UnitConversionRegistry()

    with pytest.raises(ValueError):
        registry.convert(1, "", "K")
