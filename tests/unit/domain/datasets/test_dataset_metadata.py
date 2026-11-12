"""Tests for dataset metadata."""

import pytest

from earth_twin_engine.domain.datasets import DatasetMetadata


def create_metadata(**overrides: object) -> DatasetMetadata:
    values: dict[str, object] = {
        "title": "India Daily Temperature",
        "description": "Daily near-surface temperature observations.",
        "data_format": "NetCDF",
        "license_id": "CC-BY-4.0",
        "file_size_bytes": 1024,
        "checksum_sha256": "a" * 64,
        "keywords": ("temperature", "india"),
    }
    values.update(overrides)
    return DatasetMetadata(**values)  # type: ignore[arg-type]


def test_create_valid_dataset_metadata() -> None:
    metadata = create_metadata()

    assert metadata.title == "India Daily Temperature"
    assert metadata.data_format == "NetCDF"
    assert metadata.file_size_bytes == 1024


def test_allow_optional_metadata_to_be_missing() -> None:
    metadata = create_metadata(
        data_format=None,
        license_id=None,
        file_size_bytes=None,
        checksum_sha256=None,
    )

    assert metadata.data_format is None
    assert metadata.license_id is None
    assert metadata.file_size_bytes is None
    assert metadata.checksum_sha256 is None


def test_reject_empty_title() -> None:
    with pytest.raises(ValueError, match="title"):
        create_metadata(title=" ")


def test_reject_non_string_description() -> None:
    with pytest.raises(TypeError, match="description"):
        create_metadata(description=123)


@pytest.mark.parametrize("field", ["data_format", "license_id"])
def test_reject_empty_optional_strings(field: str) -> None:
    with pytest.raises(ValueError, match=field):
        create_metadata(**{field: " "})


def test_reject_negative_file_size() -> None:
    with pytest.raises(ValueError, match="negative"):
        create_metadata(file_size_bytes=-1)


def test_reject_boolean_file_size() -> None:
    with pytest.raises(TypeError, match="integer"):
        create_metadata(file_size_bytes=True)


def test_reject_non_integer_file_size() -> None:
    with pytest.raises(TypeError, match="integer"):
        create_metadata(file_size_bytes=1.5)


@pytest.mark.parametrize(
    "checksum",
    ["", "abc", "g" * 64, "a" * 63],
)
def test_reject_invalid_sha256_checksum(checksum: str) -> None:
    with pytest.raises(ValueError, match="SHA-256"):
        create_metadata(checksum_sha256=checksum)


def test_reject_non_string_checksum() -> None:
    with pytest.raises(TypeError, match="checksum_sha256"):
        create_metadata(checksum_sha256=123)


def test_reject_mutable_keywords() -> None:
    with pytest.raises(TypeError, match="tuple"):
        create_metadata(keywords=["temperature"])


def test_reject_empty_keyword() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        create_metadata(keywords=("temperature", " "))


def test_reject_duplicate_keywords() -> None:
    with pytest.raises(ValueError, match="duplicates"):
        create_metadata(keywords=("temperature", "temperature"))


def test_dataset_metadata_is_immutable() -> None:
    metadata = create_metadata()

    with pytest.raises(AttributeError):
        metadata.title = "Changed"  # type: ignore[misc]
