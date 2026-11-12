"""Scientific trend analysis domain contracts."""

from earth_twin_engine.domain.trends.confidence_interval import (
    ConfidenceInterval,
)
from earth_twin_engine.domain.trends.regional_comparison import (
    RegionalComparison,
)
from earth_twin_engine.domain.trends.regional_trend import RegionalTrend
from earth_twin_engine.domain.trends.significance_result import (
    SignificanceResult,
)
from earth_twin_engine.domain.trends.statistical_test_result import (
    StatisticalTestResult,
)
from earth_twin_engine.domain.trends.trend_direction import TrendDirection
from earth_twin_engine.domain.trends.trend_result import TrendResult
from earth_twin_engine.domain.trends.trend_slope import TrendSlope

__all__ = [
    "ConfidenceInterval",
    "RegionalComparison",
    "RegionalTrend",
    "SignificanceResult",
    "StatisticalTestResult",
    "TrendDirection",
    "TrendResult",
    "TrendSlope",
]
