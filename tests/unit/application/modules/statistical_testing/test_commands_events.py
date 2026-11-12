"""Tests for statistical testing commands and events."""

from uuid import uuid4

import pytest

from earth_twin_engine.application.modules.statistical_testing import (
    RunStatisticalTestCommand,
    StatisticalTestCompletedEvent,
    StatisticalTestFailedEvent,
    StatisticalTestMethod,
    StatisticalTestResult,
)


def test_command_accepts_valid_configuration() -> None:
    command = RunStatisticalTestCommand(
        method=StatisticalTestMethod.MANN_KENDALL,
        series_ids=("temperature_sample",),
    )

    assert command.method == StatisticalTestMethod.MANN_KENDALL
    assert command.series_ids == ("temperature_sample",)
    assert command.significance_level == 0.05
    assert isinstance(command.command_id, type(uuid4()))


@pytest.mark.parametrize(
    "series_ids",
    [(), ("",), ("sample_one", "sample_one")],
)
def test_command_rejects_invalid_series_ids(
    series_ids: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError):
        RunStatisticalTestCommand(
            method=StatisticalTestMethod.MANN_KENDALL,
            series_ids=series_ids,
        )


def test_command_rejects_invalid_method() -> None:
    with pytest.raises(TypeError):
        RunStatisticalTestCommand(
            method="mann_kendall",  # type: ignore[arg-type]
            series_ids=("temperature_sample",),
        )


def test_completed_event_rejects_invalid_result() -> None:
    with pytest.raises(TypeError, match="StatisticalTestResult"):
        StatisticalTestCompletedEvent(
            command_id=uuid4(),
            correlation_id=None,
            result=None,  # type: ignore[arg-type]
        )


def test_failed_event_rejects_empty_method() -> None:
    with pytest.raises(ValueError, match="method"):
        StatisticalTestFailedEvent(
            command_id=uuid4(),
            correlation_id=None,
            method=" ",
            series_ids=("temperature_sample",),
            error_type="ValueError",
            error_message="Invalid test.",
        )


def test_result_rejects_inconsistent_significance() -> None:
    from datetime import UTC, datetime

    with pytest.raises(ValueError, match="significant"):
        StatisticalTestResult(
            method=StatisticalTestMethod.MANN_KENDALL,
            series_ids=("temperature_sample",),
            statistic=2.0,
            p_value=0.01,
            significance_level=0.05,
            significant=False,
            estimate=0.8,
            degrees_of_freedom=None,
            sample_sizes=(5,),
            valid_observation_counts=(5,),
            missing_observation_counts=(0,),
            confidence_interval=None,
            assumptions=("Observations are ordered in time.",),
            warnings=(),
            analyzed_at=datetime.now(UTC),
        )
