"""Tests for application module metadata."""

from dataclasses import FrozenInstanceError

import pytest

from earth_twin_engine.application.core import ModuleMetadata


def test_create_valid_module_metadata() -> None:
    metadata = ModuleMetadata(
        module_id="trend_analysis",
        name="Trend Analysis",
        version="1.0.0",
        dependencies=("time_series", "statistical_analysis"),
    )

    assert metadata.module_id == "trend_analysis"
    assert metadata.name == "Trend Analysis"
    assert metadata.version == "1.0.0"
    assert metadata.dependencies == (
        "time_series",
        "statistical_analysis",
    )


def test_create_metadata_without_dependencies() -> None:
    metadata = ModuleMetadata(
        module_id="variable_discovery",
        name="Variable Discovery",
        version="1.0.0",
    )

    assert metadata.dependencies == ()


@pytest.mark.parametrize(
    "module_id",
    [
        "",
        "TrendAnalysis",
        "1trend",
        "trend-analysis",
        "trend analysis",
    ],
)
def test_reject_invalid_module_id(module_id: str) -> None:
    with pytest.raises(ValueError, match="module_id"):
        ModuleMetadata(
            module_id=module_id,
            name="Trend Analysis",
            version="1.0.0",
        )


def test_reject_non_string_module_id() -> None:
    with pytest.raises(TypeError, match="module_id"):
        ModuleMetadata(
            module_id=123,  # type: ignore[arg-type]
            name="Trend Analysis",
            version="1.0.0",
        )


@pytest.mark.parametrize("name", ["", "   "])
def test_reject_empty_module_name(name: str) -> None:
    with pytest.raises(ValueError, match="name"):
        ModuleMetadata(
            module_id="trend_analysis",
            name=name,
            version="1.0.0",
        )


@pytest.mark.parametrize("version", ["", "   "])
def test_reject_empty_module_version(version: str) -> None:
    with pytest.raises(ValueError, match="version"):
        ModuleMetadata(
            module_id="trend_analysis",
            name="Trend Analysis",
            version=version,
        )


def test_reject_non_tuple_dependencies() -> None:
    with pytest.raises(TypeError, match="tuple"):
        ModuleMetadata(
            module_id="trend_analysis",
            name="Trend Analysis",
            version="1.0.0",
            dependencies=["time_series"],  # type: ignore[arg-type]
        )


def test_reject_non_string_dependency() -> None:
    with pytest.raises(TypeError, match="strings"):
        ModuleMetadata(
            module_id="trend_analysis",
            name="Trend Analysis",
            version="1.0.0",
            dependencies=(123,),  # type: ignore[arg-type]
        )


def test_reject_invalid_dependency_id() -> None:
    with pytest.raises(ValueError, match="invalid module ID"):
        ModuleMetadata(
            module_id="trend_analysis",
            name="Trend Analysis",
            version="1.0.0",
            dependencies=("Time-Series",),
        )


def test_reject_self_dependency() -> None:
    with pytest.raises(ValueError, match="itself"):
        ModuleMetadata(
            module_id="trend_analysis",
            name="Trend Analysis",
            version="1.0.0",
            dependencies=("trend_analysis",),
        )


def test_reject_duplicate_dependencies() -> None:
    with pytest.raises(ValueError, match="duplicates"):
        ModuleMetadata(
            module_id="trend_analysis",
            name="Trend Analysis",
            version="1.0.0",
            dependencies=("time_series", "time_series"),
        )


def test_module_metadata_is_immutable() -> None:
    metadata = ModuleMetadata(
        module_id="trend_analysis",
        name="Trend Analysis",
        version="1.0.0",
    )

    with pytest.raises(FrozenInstanceError):
        metadata.name = "Modified"  # type: ignore[misc]
