"""Scientific dataset domain entity."""

import re
from dataclasses import dataclass

from earth_twin_engine.domain.datasets.data_provenance import DataProvenance
from earth_twin_engine.domain.datasets.data_request import DataRequest
from earth_twin_engine.domain.datasets.dataset_metadata import DatasetMetadata

_DATASET_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class Dataset:
    """Represents an acquired Earth science dataset."""

    dataset_id: str
    request: DataRequest
    metadata: DatasetMetadata
    provenance: DataProvenance

    def __post_init__(self) -> None:
        if not isinstance(self.dataset_id, str):
            raise TypeError("dataset_id must be a string")

        if not _DATASET_ID_PATTERN.fullmatch(self.dataset_id):
            raise ValueError(
                "dataset_id must use lowercase letters, numbers, "
                "and underscores, starting with a letter"
            )

        if not isinstance(self.request, DataRequest):
            raise TypeError("request must be a DataRequest")

        if not isinstance(self.metadata, DatasetMetadata):
            raise TypeError("metadata must be a DatasetMetadata")

        if not isinstance(self.provenance, DataProvenance):
            raise TypeError("provenance must be a DataProvenance")

        requested_source_id = self.request.source_id
        actual_source_id = self.provenance.source.source_id

        if requested_source_id is not None and requested_source_id != actual_source_id:
            raise ValueError("provenance source does not match the requested source")

        if self.dataset_id in self.provenance.parent_dataset_ids:
            raise ValueError("dataset cannot be its own parent")
