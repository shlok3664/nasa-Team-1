"""Command handler for regional comparisons."""

from earth_twin_engine.application.events import EventDispatcher

from .commands import CompareRegionsCommand
from .events import (
    RegionalComparisonCompletedEvent,
    RegionalComparisonFailedEvent,
)
from .regional_comparison_service import RegionalComparisonService


class RegionalComparisonHandler:
    """Executes regional comparison commands and publishes their outcomes."""

    def __init__(
        self,
        service: RegionalComparisonService,
        event_dispatcher: EventDispatcher,
    ) -> None:
        if not isinstance(service, RegionalComparisonService):
            raise TypeError("service must be a RegionalComparisonService")

        if not isinstance(event_dispatcher, EventDispatcher):
            raise TypeError("event_dispatcher must be an EventDispatcher")

        self._service = service
        self._event_dispatcher = event_dispatcher

    def handle(self, command: CompareRegionsCommand):
        """Execute a regional comparison."""

        if not isinstance(command, CompareRegionsCommand):
            raise TypeError("command must be a CompareRegionsCommand")

        try:
            result = self._service.compare(
                region_ids=command.region_ids,
                variable_id=command.variable_id,
            )

            self._event_dispatcher.publish(
                RegionalComparisonCompletedEvent(
                    command_id=command.command_id,
                    correlation_id=command.correlation_id,
                    result=result,
                )
            )

            return result

        except Exception as exc:
            self._event_dispatcher.publish(
                RegionalComparisonFailedEvent(
                    command_id=command.command_id,
                    correlation_id=command.correlation_id,
                    variable_id=command.variable_id,
                    region_ids=command.region_ids,
                    error_type=type(exc).__name__,
                    error_message=str(exc) or type(exc).__name__,
                )
            )
            raise
