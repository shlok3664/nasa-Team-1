"""Command handler for statistical testing."""

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.time_series_management import (
    TimeSeriesManager,
)
from earth_twin_engine.application.modules.time_series_management.errors import (
    TimeSeriesNotFoundError,
)

from .commands import RunStatisticalTestCommand
from .errors import StatisticalTestingError
from .events import StatisticalTestCompletedEvent, StatisticalTestFailedEvent
from .statistical_test_result import StatisticalTestResult
from .statistical_testing_service import StatisticalTestingService


class StatisticalTestingHandler:
    """Coordinates statistical test execution and event publication."""

    def __init__(
        self,
        manager: TimeSeriesManager,
        service: StatisticalTestingService,
        event_dispatcher: EventDispatcher,
    ) -> None:
        if not isinstance(manager, TimeSeriesManager):
            raise TypeError("manager must be a TimeSeriesManager.")

        if not isinstance(service, StatisticalTestingService):
            raise TypeError("service must be a StatisticalTestingService.")

        if not isinstance(event_dispatcher, EventDispatcher):
            raise TypeError("event_dispatcher must be an EventDispatcher.")

        self._manager = manager
        self._service = service
        self._event_dispatcher = event_dispatcher

    def handle(self, command: RunStatisticalTestCommand) -> StatisticalTestResult:
        if not isinstance(command, RunStatisticalTestCommand):
            raise TypeError("command must be a RunStatisticalTestCommand.")

        try:
            series = tuple(self._get_series(series_id) for series_id in command.series_ids)

            result = self._service.run(
                method=command.method,
                series=series,
                significance_level=command.significance_level,
                reference_value=command.reference_value,
            )

            self._event_dispatcher.publish(
                StatisticalTestCompletedEvent(
                    command_id=command.command_id,
                    correlation_id=command.correlation_id,
                    result=result,
                )
            )
            return result

        except Exception as error:
            self._event_dispatcher.publish(
                StatisticalTestFailedEvent(
                    command_id=command.command_id,
                    correlation_id=command.correlation_id,
                    method=command.method.value,
                    series_ids=command.series_ids,
                    error_type=type(error).__name__,
                    error_message=str(error),
                )
            )
            raise

    def _get_series(self, series_id: str):
        try:
            series = self._manager.get(series_id)
        except TimeSeriesNotFoundError as error:
            raise StatisticalTestingError(f"Time series '{series_id}' was not found.") from error

        if series is None:
            raise StatisticalTestingError(f"Time series '{series_id}' was not found.")

        return series
