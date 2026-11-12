"""Coordinates Earth science dataset acquisition."""

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.data_acquisition.commands import (
    AcquireDatasetCommand,
)
from earth_twin_engine.application.modules.data_acquisition.events import (
    DatasetAcquiredEvent,
    DatasetAcquisitionFailedEvent,
)
from earth_twin_engine.application.modules.data_source_manager import DataSourceManager
from earth_twin_engine.application.modules.region_manager import RegionManager
from earth_twin_engine.application.modules.variable_discovery import VariableCatalog
from earth_twin_engine.domain.datasets import DataRequest, Dataset


class DataAcquisitionHandler:
    """Validates acquisition inputs and coordinates dataset retrieval."""

    def __init__(
        self,
        variable_catalog: VariableCatalog,
        region_manager: RegionManager,
        data_source_manager: DataSourceManager,
        event_dispatcher: EventDispatcher,
    ) -> None:
        if not isinstance(variable_catalog, VariableCatalog):
            raise TypeError("variable_catalog must be a VariableCatalog")

        if not isinstance(region_manager, RegionManager):
            raise TypeError("region_manager must be a RegionManager")

        if not isinstance(data_source_manager, DataSourceManager):
            raise TypeError("data_source_manager must be a DataSourceManager")

        if not isinstance(event_dispatcher, EventDispatcher):
            raise TypeError("event_dispatcher must be an EventDispatcher")

        self._variable_catalog = variable_catalog
        self._region_manager = region_manager
        self._data_source_manager = data_source_manager
        self._event_dispatcher = event_dispatcher

    def handle(self, command: AcquireDatasetCommand) -> Dataset:
        """Acquire a dataset for the requested variable, region, and interval."""

        if not isinstance(command, AcquireDatasetCommand):
            raise TypeError("command must be an AcquireDatasetCommand")

        try:
            variable = self._variable_catalog.get(command.variable_id)
            region = self._region_manager.get_region(command.region_id)

            request = DataRequest(
                variable=variable,
                region=region,
                temporal_range=command.temporal_range,
                temporal_resolution=command.temporal_resolution,
                source_id=command.source_id,
            )

            dataset = self._data_source_manager.retrieve(request)

        except Exception as exception:
            self._event_dispatcher.publish(
                DatasetAcquisitionFailedEvent(
                    command_id=command.command_id,
                    variable_id=command.variable_id,
                    region_id=command.region_id,
                    exception=exception,
                    correlation_id=command.correlation_id,
                )
            )
            raise

        self._event_dispatcher.publish(
            DatasetAcquiredEvent(
                command_id=command.command_id,
                dataset=dataset,
                correlation_id=command.correlation_id,
            )
        )

        return dataset
