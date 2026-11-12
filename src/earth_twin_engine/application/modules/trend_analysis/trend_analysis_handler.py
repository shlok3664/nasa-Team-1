"""Command handler for time-series trend analysis."""

from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.modules.time_series_management import (
    TimeSeriesManager,
)
from earth_twin_engine.application.modules.time_series_management.errors import (
    TimeSeriesNotFoundError,
)

from .commands import AnalyzeTimeSeriesTrendCommand
from .errors import TrendSeriesNotFoundError
from .events import TrendAnalysisCompletedEvent, TrendAnalysisFailedEvent
from .trend_analysis_result import TrendAnalysisResult
from .trend_analyzer import TrendAnalyzer


class TrendAnalysisHandler:
    """Coordinates trend analysis and publishes its outcome."""

    def __init__(
        self,
        manager: TimeSeriesManager,
        analyzer: TrendAnalyzer,
        event_dispatcher: EventDispatcher,
    ) -> None:
        if not isinstance(manager, TimeSeriesManager):
            raise TypeError("manager must be a TimeSeriesManager.")

        if not isinstance(analyzer, TrendAnalyzer):
            raise TypeError("analyzer must be a TrendAnalyzer.")

        if not isinstance(event_dispatcher, EventDispatcher):
            raise TypeError("event_dispatcher must be an EventDispatcher.")

        self._manager = manager
        self._analyzer = analyzer
        self._event_dispatcher = event_dispatcher

    def handle(
        self,
        command: AnalyzeTimeSeriesTrendCommand,
    ) -> TrendAnalysisResult:
        """Analyze a registered series and publish a completion or failure event."""

        if not isinstance(command, AnalyzeTimeSeriesTrendCommand):
            raise TypeError("command must be an AnalyzeTimeSeriesTrendCommand.")

        try:
            try:
                series = self._manager.get(command.series_id)
            except TimeSeriesNotFoundError as error:
                raise TrendSeriesNotFoundError(
                    f"Time series '{command.series_id}' was not found."
                ) from error

            if series is None:
                raise TrendSeriesNotFoundError(f"Time series '{command.series_id}' was not found.")

            result = self._analyzer.analyze(series)

            self._event_dispatcher.publish(
                TrendAnalysisCompletedEvent(
                    command_id=command.command_id,
                    correlation_id=command.correlation_id,
                    result=result,
                )
            )
            return result

        except Exception as error:
            self._event_dispatcher.publish(
                TrendAnalysisFailedEvent(
                    command_id=command.command_id,
                    correlation_id=command.correlation_id,
                    series_id=command.series_id,
                    error_type=type(error).__name__,
                    error_message=str(error),
                )
            )
            raise
