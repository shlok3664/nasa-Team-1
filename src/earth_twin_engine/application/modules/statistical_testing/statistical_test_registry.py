"""Thread-safe registry for statistical test implementations."""

from threading import RLock

from .errors import (
    DuplicateStatisticalTestError,
    StatisticalTestNotFoundError,
)
from .statistical_test import StatisticalTest
from .statistical_test_method import StatisticalTestMethod


class StatisticalTestRegistry:
    """Registers and resolves statistical test implementations."""

    def __init__(self) -> None:
        self._tests: dict[StatisticalTestMethod, StatisticalTest] = {}
        self._lock = RLock()

    def register(self, statistical_test: StatisticalTest) -> None:
        if not isinstance(statistical_test.method, StatisticalTestMethod):
            raise TypeError("A statistical test must expose a valid method.")

        with self._lock:
            if statistical_test.method in self._tests:
                raise DuplicateStatisticalTestError(
                    f"Test '{statistical_test.method.value}' is already registered."
                )

            self._tests[statistical_test.method] = statistical_test

    def unregister(self, method: StatisticalTestMethod) -> bool:
        with self._lock:
            return self._tests.pop(method, None) is not None

    def get(self, method: StatisticalTestMethod) -> StatisticalTest:
        if not isinstance(method, StatisticalTestMethod):
            raise TypeError("method must be a StatisticalTestMethod.")

        with self._lock:
            statistical_test = self._tests.get(method)

        if statistical_test is None:
            raise StatisticalTestNotFoundError(
                f"Statistical test '{method.value}' is not registered."
            )

        return statistical_test

    def get_all(self) -> tuple[StatisticalTestMethod, ...]:
        with self._lock:
            return tuple(self._tests)

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._tests)
