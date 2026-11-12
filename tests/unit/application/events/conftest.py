from dataclasses import dataclass

import pytest

from earth_twin_engine.application.events import (
    ApplicationEvent,
    EventDispatcher,
)


@dataclass(frozen=True, slots=True)
class DatasetRetrieved(ApplicationEvent):
    dataset_id: str = "dataset_001"


@dataclass(frozen=True, slots=True)
class DatasetValidated(ApplicationEvent):
    dataset_id: str = "dataset_001"


@dataclass(frozen=True, slots=True)
class SpecializedDatasetRetrieved(DatasetRetrieved):
    source_name: str = "NASA"


@pytest.fixture
def dispatcher() -> EventDispatcher:
    return EventDispatcher()


@pytest.fixture
def dataset_event() -> DatasetRetrieved:
    return DatasetRetrieved(dataset_id="dataset_123")
