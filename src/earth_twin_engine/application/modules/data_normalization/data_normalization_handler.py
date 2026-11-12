"""Coordinates scientific dataset normalization."""

from earth_twin_engine.application.events import EventDispatcher

from .commands import NormalizeDatasetCommand
from .data_normalizer import DataNormalizer
from .events import DatasetNormalizedEvent
from .normalization_result import NormalizationResult


class DataNormalizationHandler:
    """Handles dataset normalization commands."""

    def __init__(
        self,
        normalizer: DataNormalizer,
        event_dispatcher: EventDispatcher,
    ) -> None:
        if not isinstance(normalizer, DataNormalizer):
            raise TypeError("normalizer must be a DataNormalizer instance.")

        if not isinstance(event_dispatcher, EventDispatcher):
            raise TypeError("event_dispatcher must be an EventDispatcher instance.")

        self._normalizer = normalizer
        self._event_dispatcher = event_dispatcher

    def handle(self, command: NormalizeDatasetCommand) -> NormalizationResult:
        """Normalize a dataset, publish the result, and return it."""

        if not isinstance(command, NormalizeDatasetCommand):
            raise TypeError("command must be a NormalizeDatasetCommand instance.")

        result = self._normalizer.normalize(
            dataset=command.dataset,
            time_series=command.time_series,
        )

        self._event_dispatcher.publish(
            DatasetNormalizedEvent(
                command_id=command.command_id,
                correlation_id=command.correlation_id,
                dataset_id=result.dataset.dataset_id,
                normalization_result=result,
            )
        )

        return result
