"""Tests for scientific analysis report contracts."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from earth_twin_engine.domain.reports import AnalysisReport
from earth_twin_engine.domain.temporal import TemporalRange
from earth_twin_engine.domain.trends import (
    TrendDirection,
    TrendResult,
    TrendSlope,
)


@pytest.fixture
def report_generated_at() -> datetime:
    return datetime(2026, 11, 11, 12, 0, tzinfo=UTC)


@pytest.fixture
def report_trend(
    trend_variable,
    trend_region,
    trend_range,
) -> TrendResult:
    return TrendResult(
        variable=trend_variable,
        region=trend_region,
        temporal_range=trend_range,
        slope=TrendSlope(0.25, "K/year"),
        direction=TrendDirection.INCREASING,
        sample_count=20,
    )


def create_report(**overrides: object) -> AnalysisReport:
    values: dict[str, object] = {
        "report_id": "temperature-report-001",
        "title": "Regional Temperature Analysis",
        "summary": "Temperature increased during the study period.",
        "generated_at": datetime(2026, 11, 11, 12, 0, tzinfo=UTC),
        "temporal_range": None,
        "trend_results": (),
        "dataset_ids": (),
        "limitations": (),
    }
    values.update(overrides)
    return AnalysisReport(**values)  # type: ignore[arg-type]


def test_create_valid_analysis_report(
    report_generated_at,
    trend_range,
    report_trend,
) -> None:
    report = create_report(
        generated_at=report_generated_at,
        temporal_range=trend_range,
        trend_results=(report_trend,),
        dataset_ids=("nasa-temperature-dataset",),
        limitations=("Observations contain seasonal gaps.",),
    )

    assert report.report_id == "temperature-report-001"
    assert report.title == "Regional Temperature Analysis"
    assert report.generated_at == report_generated_at
    assert report.temporal_range == trend_range
    assert report.trend_results == (report_trend,)
    assert report.dataset_ids == ("nasa-temperature-dataset",)
    assert report.limitations == ("Observations contain seasonal gaps.",)


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("report_id", None, "report_id must be a string"),
        ("temporal_range", None, "TemporalRange"),
        ("trend_results", [], "tuple"),
        ("dataset_ids", [], "tuple"),
        ("limitations", [], "tuple"),
    ],
)
def test_reject_invalid_contract_types(
    trend_range,
    report_trend,
    field: str,
    value: object,
    expected_error: str,
) -> None:
    values: dict[str, object] = {
        "temporal_range": trend_range,
        "trend_results": (report_trend,),
    }
    values[field] = value

    with pytest.raises((TypeError, ValueError), match=expected_error):
        create_report(**values)


@pytest.mark.parametrize(
    "report_id",
    [
        "",
        "Temperature",
        "1-report",
        "report with spaces",
        "report@001",
    ],
)
def test_reject_invalid_report_id(report_id: str) -> None:
    with pytest.raises(ValueError, match="report_id"):
        create_report(report_id=report_id)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", ""),
        ("title", "   "),
        ("summary", ""),
        ("summary", "   "),
    ],
)
def test_reject_empty_text_fields(field: str, value: str) -> None:
    with pytest.raises(ValueError, match=field):
        create_report(**{field: value})


def test_reject_naive_generated_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        create_report(generated_at=datetime(2026, 11, 11, 12, 0))


def test_reject_non_datetime_generated_at() -> None:
    with pytest.raises(TypeError, match="datetime"):
        create_report(generated_at="2026-11-11")  # type: ignore[arg-type]


def test_reject_empty_trend_results(trend_range) -> None:
    with pytest.raises(ValueError, match="at least one trend"):
        create_report(
            temporal_range=trend_range,
            trend_results=(),
        )


def test_reject_invalid_trend_result_type(trend_range) -> None:
    with pytest.raises(TypeError, match="TrendResult"):
        create_report(
            temporal_range=trend_range,
            trend_results=("not-a-trend",),
        )


def test_reject_trend_with_different_temporal_range(
    trend_variable,
    trend_region,
    trend_range,
) -> None:
    different_range = TemporalRange(
        start=datetime(2000, 1, 1, tzinfo=UTC),
        end=datetime(2010, 1, 1, tzinfo=UTC),
    )

    different_trend = TrendResult(
        variable=trend_variable,
        region=trend_region,
        temporal_range=different_range,
        slope=TrendSlope(0.2, "K/year"),
        direction=TrendDirection.INCREASING,
        sample_count=10,
    )

    with pytest.raises(ValueError, match="report temporal range"):
        create_report(
            temporal_range=trend_range,
            trend_results=(different_trend,),
        )


def test_reject_duplicate_variable_region_findings(
    trend_variable,
    trend_region,
    trend_range,
    report_trend,
) -> None:
    duplicate = TrendResult(
        variable=trend_variable,
        region=trend_region,
        temporal_range=trend_range,
        slope=TrendSlope(0.3, "K/year"),
        direction=TrendDirection.INCREASING,
        sample_count=15,
    )

    with pytest.raises(ValueError, match="duplicate"):
        create_report(
            temporal_range=trend_range,
            trend_results=(report_trend, duplicate),
        )


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("dataset_ids", (1,), "strings"),
        ("dataset_ids", ("",), "empty strings"),
        ("dataset_ids", ("dataset-1", "dataset-1"), "duplicates"),
        ("limitations", (1,), "strings"),
        ("limitations", ("",), "empty strings"),
        ("limitations", ("gap", "gap"), "duplicates"),
    ],
)
def test_reject_invalid_report_collections(
    trend_range,
    report_trend,
    field: str,
    value: tuple[object, ...],
    expected_error: str,
) -> None:
    with pytest.raises((TypeError, ValueError), match=expected_error):
        create_report(
            temporal_range=trend_range,
            trend_results=(report_trend,),
            **{field: value},
        )


def test_analysis_report_is_immutable(
    trend_range,
    report_trend,
) -> None:
    report = create_report(
        temporal_range=trend_range,
        trend_results=(report_trend,),
    )

    with pytest.raises(FrozenInstanceError):
        report.title = "Modified report"  # type: ignore[misc]
