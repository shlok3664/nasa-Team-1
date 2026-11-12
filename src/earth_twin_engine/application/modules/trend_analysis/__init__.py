"""Scientific time-series trend analysis module."""

from .commands import AnalyzeTimeSeriesTrendCommand
from .errors import (
    InsufficientTrendDataError,
    InvalidTrendConfigurationError,
    TrendAnalysisError,
    TrendSeriesNotFoundError,
)
from .events import TrendAnalysisCompletedEvent, TrendAnalysisFailedEvent
from .trend_analysis_handler import TrendAnalysisHandler
from .trend_analysis_module import TrendAnalysisModule
from .trend_analysis_result import (
    TrendAnalysisResult,
    TrendDirection,
    TrendStrength,
)
from .trend_analyzer import TrendAnalyzer

__all__ = [
    "AnalyzeTimeSeriesTrendCommand",
    "InsufficientTrendDataError",
    "InvalidTrendConfigurationError",
    "TrendAnalysisCompletedEvent",
    "TrendAnalysisError",
    "TrendAnalysisFailedEvent",
    "TrendAnalysisHandler",
    "TrendAnalysisModule",
    "TrendAnalysisResult",
    "TrendAnalyzer",
    "TrendDirection",
    "TrendSeriesNotFoundError",
    "TrendStrength",
]
