"""Coordinates scientific dataset validation."""

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.data_validation.commands import (
    ValidateDatasetCommand,
)
from earth_twin_engine.application.modules.data_validation.dataset_validator import (
    DatasetValidator,
)
from earth_twin_engine.application.modules.data_validation.events import (
    DatasetValidatedEvent,
)
from earth_twin_engine.application.modules.data_validation.validation_result import (
    ValidationResult,
)


class DataValidationHandler:
    """Handles dataset validation commands."""

    def __init__(
        self,
        validator: DatasetValidator,
        event_dispatcher: EventDispatcher,
    ) -> None:
        if not isinstance(validator, DatasetValidator):
            raise TypeError("validator must be a DatasetValidator instance.")

        if not isinstance(event_dispatcher, EventDispatcher):
            raise TypeError("event_dispatcher must be an EventDispatcher instance.")

        self._validator = validator
        self._event_dispatcher = event_dispatcher

    def handle(self, command: ValidateDatasetCommand) -> ValidationResult:
        """Validate a dataset, publish its result, and return that result."""

        if not isinstance(command, ValidateDatasetCommand):
            raise TypeError("command must be a ValidateDatasetCommand instance.")

        result = self._validator.validate(
            dataset=command.dataset,
            time_series=command.time_series,
        )

        self._event_dispatcher.publish(
            DatasetValidatedEvent(
                command_id=command.command_id,
                correlation_id=command.correlation_id,
                dataset_id=command.dataset.dataset_id,
                validation_result=result,
            )
        )

        return result
