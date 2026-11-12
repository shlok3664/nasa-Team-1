import pytest

from earth_twin_engine.application.modules.variable_discovery import VariableCatalog
from earth_twin_engine.application.modules.variable_discovery.queries import (
    DiscoverEarthVariablesQuery,
    GetEarthVariableQuery,
)
from earth_twin_engine.application.modules.variable_discovery.query_handlers import (
    DiscoverEarthVariablesHandler,
    GetEarthVariableHandler,
)


def test_get_variable_handler_returns_variable(temperature_variable) -> None:
    catalog = VariableCatalog((temperature_variable,))
    handler = GetEarthVariableHandler(catalog)

    result = handler.handle(GetEarthVariableQuery(variable_id="air_temperature"))

    assert result is temperature_variable


def test_get_variable_handler_propagates_missing_variable() -> None:
    handler = GetEarthVariableHandler(VariableCatalog())

    with pytest.raises(KeyError):
        handler.handle(GetEarthVariableQuery(variable_id="unknown"))


def test_discover_handler_returns_filtered_variables(
    temperature_variable,
    precipitation_variable,
) -> None:
    catalog = VariableCatalog((temperature_variable, precipitation_variable))
    handler = DiscoverEarthVariablesHandler(catalog)

    result = handler.handle(DiscoverEarthVariablesQuery())

    assert result == (
        temperature_variable,
        precipitation_variable,
    )


def test_discover_handler_applies_filters(
    temperature_variable,
    precipitation_variable,
) -> None:
    catalog = VariableCatalog((temperature_variable, precipitation_variable))
    handler = DiscoverEarthVariablesHandler(catalog)

    result = handler.handle(DiscoverEarthVariablesQuery(keyword="rainfall"))

    assert result == (precipitation_variable,)


def test_handlers_reject_invalid_catalog() -> None:
    with pytest.raises(TypeError):
        GetEarthVariableHandler(object())  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        DiscoverEarthVariablesHandler(object())  # type: ignore[arg-type]


def test_get_handler_rejects_invalid_query(temperature_variable) -> None:
    handler = GetEarthVariableHandler(VariableCatalog((temperature_variable,)))

    with pytest.raises(TypeError):
        handler.handle(object())  # type: ignore[arg-type]


def test_discover_handler_rejects_invalid_query() -> None:
    handler = DiscoverEarthVariablesHandler(VariableCatalog())

    with pytest.raises(TypeError):
        handler.handle(object())  # type: ignore[arg-type]
