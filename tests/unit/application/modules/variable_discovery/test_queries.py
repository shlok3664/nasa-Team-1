from uuid import uuid4

import pytest

from earth_twin_engine.application.modules.variable_discovery.queries import (
    DiscoverEarthVariablesQuery,
    GetEarthVariableQuery,
)
from earth_twin_engine.domain.temporal.temporal_resolution import (
    TemporalResolution,
)
from earth_twin_engine.domain.variables.variable_category import VariableCategory


def test_get_variable_query() -> None:
    query = GetEarthVariableQuery(variable_id="air_temperature")

    assert query.variable_id == "air_temperature"
    assert query.query_id is not None
    assert query.issued_at.tzinfo is not None


def test_get_variable_query_preserves_correlation_id() -> None:
    correlation_id = uuid4()

    query = GetEarthVariableQuery(
        variable_id="air_temperature",
        correlation_id=correlation_id,
    )

    assert query.correlation_id == correlation_id


@pytest.mark.parametrize("variable_id", ["", " "])
def test_reject_invalid_variable_id(variable_id: str) -> None:
    with pytest.raises(ValueError):
        GetEarthVariableQuery(variable_id=variable_id)


def test_reject_non_string_variable_id() -> None:
    with pytest.raises(TypeError):
        GetEarthVariableQuery(variable_id=123)  # type: ignore[arg-type]


def test_discovery_query_defaults() -> None:
    query = DiscoverEarthVariablesQuery()

    assert query.category is None
    assert query.keyword is None
    assert query.temporal_resolution is None
    assert query.source_id is None


def test_discovery_query_accepts_all_filters() -> None:
    query = DiscoverEarthVariablesQuery(
        category=VariableCategory.ATMOSPHERE,
        keyword="temperature",
        temporal_resolution=TemporalResolution.DAILY,
        source_id="nasa_merra2",
    )

    assert query.category is VariableCategory.ATMOSPHERE
    assert query.keyword == "temperature"
    assert query.temporal_resolution is TemporalResolution.DAILY
    assert query.source_id == "nasa_merra2"


def test_reject_invalid_category() -> None:
    with pytest.raises(TypeError):
        DiscoverEarthVariablesQuery(
            category="atmosphere"  # type: ignore[arg-type]
        )


def test_reject_invalid_temporal_resolution() -> None:
    with pytest.raises(TypeError):
        DiscoverEarthVariablesQuery(
            temporal_resolution="daily"  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("keyword", ["", " "])
def test_reject_invalid_keyword(keyword: str) -> None:
    with pytest.raises(ValueError):
        DiscoverEarthVariablesQuery(keyword=keyword)


def test_reject_non_string_keyword() -> None:
    with pytest.raises(TypeError):
        DiscoverEarthVariablesQuery(keyword=123)  # type: ignore[arg-type]


@pytest.mark.parametrize("source_id", ["", " "])
def test_reject_invalid_source_id(source_id: str) -> None:
    with pytest.raises(ValueError):
        DiscoverEarthVariablesQuery(source_id=source_id)


def test_reject_non_string_source_id() -> None:
    with pytest.raises(TypeError):
        DiscoverEarthVariablesQuery(source_id=123)  # type: ignore[arg-type]
