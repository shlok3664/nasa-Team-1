"""Scientific dataset provenance."""

from dataclasses import dataclass
from datetime import UTC, datetime

from earth_twin_engine.domain.datasets.data_source import DataSource


@dataclass(frozen=True, slots=True)
class DataProvenance:
    """Records the origin and processing history of a dataset."""

    source: DataSource
    retrieved_at: datetime
    source_record_id: str | None = None
    transformations: tuple[str, ...] = ()
    parent_dataset_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.source, DataSource):
            raise TypeError("source must be a DataSource")

        if not isinstance(self.retrieved_at, datetime):
            raise TypeError("retrieved_at must be a datetime")

        if self.retrieved_at.tzinfo is None or self.retrieved_at.utcoffset() is None:
            raise ValueError("retrieved_at must be timezone-aware")

        if self.source_record_id is not None:
            if not isinstance(self.source_record_id, str) or not self.source_record_id.strip():
                raise ValueError("source_record_id must be a non-empty string")

        self._validate_string_collection(
            self.transformations,
            "transformations",
        )
        self._validate_string_collection(
            self.parent_dataset_ids,
            "parent_dataset_ids",
        )

    @property
    def retrieved_at_utc(self) -> datetime:
        """Return the retrieval timestamp normalized to UTC."""

        return self.retrieved_at.astimezone(UTC)

    @staticmethod
    def _validate_string_collection(
        values: tuple[str, ...],
        field_name: str,
    ) -> None:
        if not isinstance(values, tuple):
            raise TypeError(f"{field_name} must be a tuple")

        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError(f"{field_name} must contain non-empty strings")

        if len(set(values)) != len(values):
            raise ValueError(f"{field_name} must not contain duplicates")
