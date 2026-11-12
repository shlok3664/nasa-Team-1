"""Scientific statistical testing application module."""

from .commands import RunStatisticalTestCommand
from .errors import (
    DuplicateStatisticalTestError,
    IncompatibleStatisticalSamplesError,
    InsufficientStatisticalDataError,
    InvalidStatisticalTestConfigurationError,
    StatisticalTestingError,
    StatisticalTestNotFoundError,
)
from .events import StatisticalTestCompletedEvent, StatisticalTestFailedEvent
from .statistical_test import (
    MannKendallTest,
    OneSampleTTest,
    StatisticalTest,
    WelchTTest,
)
from .statistical_test_method import StatisticalTestMethod
from .statistical_test_registry import StatisticalTestRegistry
from .statistical_test_result import StatisticalTestResult
from .statistical_testing_handler import StatisticalTestingHandler
from .statistical_testing_module import StatisticalTestingModule
from .statistical_testing_service import StatisticalTestingService

__all__ = [
    "DuplicateStatisticalTestError",
    "IncompatibleStatisticalSamplesError",
    "InsufficientStatisticalDataError",
    "InvalidStatisticalTestConfigurationError",
    "MannKendallTest",
    "OneSampleTTest",
    "RunStatisticalTestCommand",
    "StatisticalTest",
    "StatisticalTestCompletedEvent",
    "StatisticalTestFailedEvent",
    "StatisticalTestMethod",
    "StatisticalTestNotFoundError",
    "StatisticalTestRegistry",
    "StatisticalTestResult",
    "StatisticalTestingError",
    "StatisticalTestingHandler",
    "StatisticalTestingModule",
    "StatisticalTestingService",
    "WelchTTest",
]
