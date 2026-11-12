"""Tests for scientific variable metadata."""

import pytest

from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.variables import VariableMetadata


def create_metadata(**overrides: object) -> VariableMetadata:
    values: dict[str, object] = {
        "unit": "K",
        "temporal_resolutions": (
            TemporalResolution.DAILY,
            TemporalResolution.MONTHLY,
        ),
        "spatial_resolution_meters": 1000.0,
        "keywords": ("temperature", "atmosphere"),
        "source_ids": ("nasa_source_1",),
    }
    values.update(overrides)
    return VariableMetadata(**values)  # type: ignore[arg-type]


def test_create_valid_metadata() -> None:
    metadata = create_metadata()

    assert metadata.unit == "K"
    assert TemporalResolution.DAILY in metadata.temporal_resolutions
    assert metadata.spatial_resolution_meters == 1000.0


def test_allow_missing_spatial_resolution() -> None:
    metadata = create_metadata(spatial_resolution_meters=None)

    assert metadata.spatial_resolution_meters is None


def test_reject_empty_unit() -> None:
    with pytest.raises(ValueError, match="unit"):
        create_metadata(unit=" ")


def test_reject_empty_temporal_resolutions() -> None:
    with pytest.raises(ValueError, match="at least one"):
        create_metadata(temporal_resolutions=())


def test_reject_invalid_temporal_resolution() -> None:
    with pytest.raises(TypeError, match="TemporalResolution"):
        create_metadata(temporal_resolutions=("daily",))


def test_reject_duplicate_temporal_resolutions() -> None:
    with pytest.raises(ValueError, match="duplicates"):
        create_metadata(
            temporal_resolutions=(
                TemporalResolution.DAILY,
                TemporalResolution.DAILY,
            )
        )


@pytest.mark.parametrize("resolution", [0, -1, float("inf"), float("nan")])
def test_reject_invalid_spatial_resolution(resolution: float) -> None:
    with pytest.raises(ValueError, match="finite and positive"):
        create_metadata(spatial_resolution_meters=resolution)


def test_reject_boolean_spatial_resolution() -> None:
    with pytest.raises(TypeError, match="numeric value"):
        create_metadata(spatial_resolution_meters=True)


def test_reject_mutable_keywords() -> None:
    with pytest.raises(TypeError, match="keywords must be a tuple"):
        create_metadata(keywords=["temperature"])


def test_reject_duplicate_source_ids() -> None:
    with pytest.raises(ValueError, match="duplicates"):
        create_metadata(source_ids=("nasa", "nasa"))


def test_metadata_is_immutable() -> None:
    metadata = create_metadata()

    with pytest.raises(AttributeError):
        metadata.unit = "C"  # type: ignore[misc]
