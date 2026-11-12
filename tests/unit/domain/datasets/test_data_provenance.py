"""Tests for dataset provenance."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from earth_twin_engine.domain.datasets import DataProvenance, DataSource


def create_provenance(**overrides: object) -> DataProvenance:
    values: dict[str, object] = {
        "source": DataSource("nasa_merra2", "MERRA-2", "NASA"),
        "retrieved_at": datetime(2026, 1, 1, tzinfo=UTC),
        "source_record_id": "record_123",
        "transformations": ("unit_conversion", "quality_filter"),
        "parent_dataset_ids": ("raw_temperature",),
    }
    values.update(overrides)
    return DataProvenance(**values)  # type: ignore[arg-type]


def test_create_valid_provenance() -> None:
    provenance = create_provenance()
    assert provenance.source.source_id == "nasa_merra2"
    assert provenance.source_record_id == "record_123"
    assert len(provenance.transformations) == 2


def test_reject_invalid_source() -> None:
    with pytest.raises(TypeError, match="DataSource"):
        create_provenance(source=None)


def test_reject_non_datetime_retrieval_time() -> None:
    with pytest.raises(TypeError, match="datetime"):
        create_provenance(retrieved_at="2026-01-01")


def test_reject_naive_retrieval_time() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        create_provenance(retrieved_at=datetime(2026, 1, 1))


def test_normalize_retrieval_time_to_utc() -> None:
    local_time = datetime(
        2026,
        1,
        1,
        5,
        30,
        tzinfo=timezone(timedelta(hours=5, minutes=30)),
    )
    provenance = create_provenance(retrieved_at=local_time)

    assert provenance.retrieved_at_utc == datetime(2026, 1, 1, tzinfo=UTC)


def test_allow_missing_source_record_id() -> None:
    assert create_provenance(source_record_id=None).source_record_id is None


@pytest.mark.parametrize("field", ["transformations", "parent_dataset_ids"])
def test_reject_mutable_collections(field: str) -> None:
    with pytest.raises(TypeError, match="tuple"):
        create_provenance(**{field: ["value"]})


@pytest.mark.parametrize("field", ["transformations", "parent_dataset_ids"])
def test_reject_empty_collection_values(field: str) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        create_provenance(**{field: ("valid", " ")})


@pytest.mark.parametrize("field", ["transformations", "parent_dataset_ids"])
def test_reject_duplicate_collection_values(field: str) -> None:
    with pytest.raises(ValueError, match="duplicates"):
        create_provenance(**{field: ("same", "same")})


def test_reject_empty_source_record_id() -> None:
    with pytest.raises(ValueError, match="source_record_id"):
        create_provenance(source_record_id=" ")


def test_provenance_is_immutable() -> None:
    provenance = create_provenance()

    with pytest.raises(AttributeError):
        provenance.source_record_id = "changed"  # type: ignore[misc]
