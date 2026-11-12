"""Tests for scientific data sources."""

import pytest

from earth_twin_engine.domain.datasets import DataSource


def create_source(**overrides: object) -> DataSource:
    values: dict[str, object] = {
        "source_id": "nasa_merra2",
        "name": "MERRA-2",
        "provider": "NASA",
        "description": "Modern-Era Retrospective Analysis for Research and Applications.",
        "homepage_url": "https://example.com",
    }
    values.update(overrides)
    return DataSource(**values)  # type: ignore[arg-type]


def test_create_valid_data_source() -> None:
    source = create_source()

    assert source.source_id == "nasa_merra2"
    assert source.name == "MERRA-2"
    assert source.provider == "NASA"


@pytest.mark.parametrize(
    "source_id",
    ["", "NASA", "nasa-source", "1nasa", "nasa source"],
)
def test_reject_invalid_source_id(source_id: str) -> None:
    with pytest.raises(ValueError, match="source_id"):
        create_source(source_id=source_id)


def test_reject_non_string_source_id() -> None:
    with pytest.raises(TypeError, match="source_id"):
        create_source(source_id=123)


@pytest.mark.parametrize("field", ["name", "provider"])
def test_reject_empty_required_fields(field: str) -> None:
    with pytest.raises(ValueError, match=field):
        create_source(**{field: " "})


def test_reject_non_string_description() -> None:
    with pytest.raises(TypeError, match="description"):
        create_source(description=123)


def test_reject_invalid_homepage_url() -> None:
    with pytest.raises(ValueError, match="HTTP or HTTPS"):
        create_source(homepage_url="ftp://example.com")


def test_reject_non_string_homepage_url() -> None:
    with pytest.raises(TypeError, match="homepage_url"):
        create_source(homepage_url=123)


def test_allow_missing_homepage_url() -> None:
    source = create_source(homepage_url=None)

    assert source.homepage_url is None


def test_data_source_is_immutable() -> None:
    source = create_source()

    with pytest.raises(AttributeError):
        source.name = "Changed"  # type: ignore[misc]
