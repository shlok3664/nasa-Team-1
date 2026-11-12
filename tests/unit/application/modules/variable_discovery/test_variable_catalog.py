import pytest

from earth_twin_engine.application.modules.variable_discovery import VariableCatalog
from earth_twin_engine.domain.temporal.temporal_resolution import (
    TemporalResolution,
)
from earth_twin_engine.domain.variables.variable_category import VariableCategory


def test_register_and_retrieve_variable(temperature_variable) -> None:
    catalog = VariableCatalog()
    catalog.register(temperature_variable)

    assert catalog.get("air_temperature") is temperature_variable
    assert catalog.find("air_temperature") is temperature_variable
    assert catalog.variable_count == 1


def test_reject_duplicate_variable_id(temperature_variable) -> None:
    catalog = VariableCatalog((temperature_variable,))

    with pytest.raises(ValueError, match="already registered"):
        catalog.register(temperature_variable)


def test_reject_invalid_variable_type() -> None:
    catalog = VariableCatalog()

    with pytest.raises(TypeError):
        catalog.register("temperature")  # type: ignore[arg-type]


def test_get_missing_variable_raises_key_error() -> None:
    catalog = VariableCatalog()

    with pytest.raises(KeyError, match="not registered"):
        catalog.get("unknown_variable")


def test_find_missing_variable_returns_none() -> None:
    assert VariableCatalog().find("unknown_variable") is None


def test_unregister_variable(temperature_variable) -> None:
    catalog = VariableCatalog((temperature_variable,))

    assert catalog.unregister("air_temperature") is True
    assert catalog.unregister("air_temperature") is False
    assert catalog.variable_count == 0


def test_reject_invalid_variable_id() -> None:
    catalog = VariableCatalog()

    with pytest.raises(ValueError):
        catalog.get(" ")

    with pytest.raises(TypeError):
        catalog.find(None)  # type: ignore[arg-type]


def test_constructor_registers_initial_variables(
    temperature_variable,
    precipitation_variable,
) -> None:
    catalog = VariableCatalog((temperature_variable, precipitation_variable))

    assert catalog.variable_count == 2


def test_discover_all_returns_sorted_results(
    temperature_variable,
    precipitation_variable,
    vegetation_variable,
) -> None:
    catalog = VariableCatalog(
        (
            vegetation_variable,
            temperature_variable,
            precipitation_variable,
        )
    )

    results = catalog.all()

    assert tuple(item.variable_id for item in results) == (
        "air_temperature",
        "precipitation",
        "vegetation_index",
    )


def test_discover_by_category(
    temperature_variable,
    precipitation_variable,
) -> None:
    catalog = VariableCatalog((temperature_variable, precipitation_variable))

    results = catalog.discover(category=VariableCategory.ATMOSPHERE)

    assert results == (temperature_variable,)


def test_discover_by_keyword(
    temperature_variable,
    precipitation_variable,
    vegetation_variable,
) -> None:
    catalog = VariableCatalog(
        (
            temperature_variable,
            precipitation_variable,
            vegetation_variable,
        )
    )

    results = catalog.discover(keyword="SATELLITE")

    assert results == (vegetation_variable,)


def test_discover_by_temporal_resolution(
    temperature_variable,
    precipitation_variable,
    vegetation_variable,
) -> None:
    catalog = VariableCatalog(
        (
            temperature_variable,
            precipitation_variable,
            vegetation_variable,
        )
    )

    results = catalog.discover(temporal_resolution=TemporalResolution.HOURLY)

    assert results == (temperature_variable,)


def test_discover_by_source(
    temperature_variable,
    precipitation_variable,
    vegetation_variable,
) -> None:
    catalog = VariableCatalog(
        (
            temperature_variable,
            precipitation_variable,
            vegetation_variable,
        )
    )

    results = catalog.discover(source_id="NASA_GPM")

    assert results == (precipitation_variable,)


def test_discover_combined_filters(
    temperature_variable,
    precipitation_variable,
    vegetation_variable,
) -> None:
    catalog = VariableCatalog(
        (
            temperature_variable,
            precipitation_variable,
            vegetation_variable,
        )
    )

    results = catalog.discover(
        category=VariableCategory.ATMOSPHERE,
        keyword="weather",
        temporal_resolution=TemporalResolution.HOURLY,
        source_id="nasa_merra2",
    )

    assert results == (temperature_variable,)


def test_discover_with_no_matches_returns_empty_tuple(
    temperature_variable,
) -> None:
    catalog = VariableCatalog((temperature_variable,))

    assert catalog.discover(keyword="ocean") == ()


@pytest.mark.parametrize("keyword", ["", " "])
def test_reject_empty_keyword(temperature_variable, keyword: str) -> None:
    catalog = VariableCatalog((temperature_variable,))

    with pytest.raises(ValueError):
        catalog.discover(keyword=keyword)


def test_reject_invalid_discovery_filters() -> None:
    catalog = VariableCatalog()

    with pytest.raises(TypeError):
        catalog.discover(category="atmosphere")  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        catalog.discover(
            temporal_resolution="daily"  # type: ignore[arg-type]
        )

    with pytest.raises(TypeError):
        catalog.discover(source_id=123)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        catalog.discover(source_id=" ")
