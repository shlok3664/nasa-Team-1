"""HTTP API for the Earth Twin Engine statistical analysis model."""

from __future__ import annotations

import os
from datetime import datetime
from statistics import fmean
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from earth_twin_engine.application.modules.trend_analysis import TrendAnalyzer
from earth_twin_engine.application.modules.trend_analysis.trend_analysis_result import (
    TrendAnalysisResult,
)
from earth_twin_engine.domain.geography import SpatialCoordinate
from earth_twin_engine.domain.temporal import TemporalResolution
from earth_twin_engine.domain.time_series import TimeSeries, TimeSeriesPoint
from earth_twin_engine.domain.variables import (
    EarthVariable,
    VariableCategory,
    VariableMetadata,
)


class ObservationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: AwareDatetime
    value: float | None = Field(default=None, allow_inf_nan=False)


class RegionalSeriesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    region_id: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=64)
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)
    observations: list[ObservationInput] = Field(min_length=1, max_length=5000)


class TrendBatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variable_id: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=64)
    variable_name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)
    unit: str = Field(min_length=1, max_length=32)
    category: VariableCategory
    temporal_resolution: TemporalResolution
    significance_level: float = Field(default=0.05, gt=0, lt=1, allow_inf_nan=False)
    series: list[RegionalSeriesInput] = Field(min_length=1, max_length=10)


class TrendSeriesOutput(BaseModel):
    region_id: str
    direction: str
    strength: str
    input_observation_count: int
    valid_observation_count: int
    missing_observation_count: int
    linear_slope_per_day: float | None
    linear_slope_per_period: float | None
    sen_slope_per_day: float | None
    sen_slope_per_period: float | None
    average_interval_days: float | None
    net_change: float | None
    average: float | None
    r_squared: float | None
    kendall_tau: float | None
    p_value: float | None
    significance_level: float
    is_significant: bool | None
    analyzed_at: datetime


class TrendBatchOutput(BaseModel):
    model: Literal["TrendAnalyzer"]
    method: Literal["ordinary_least_squares+sen_slope+mann_kendall"]
    results: list[TrendSeriesOutput]


class HealthOutput(BaseModel):
    status: Literal["ok"]
    model: Literal["TrendAnalyzer"]


def _analyze_series(
    payload: RegionalSeriesInput,
    request: TrendBatchInput,
    analyzer: TrendAnalyzer,
) -> TrendSeriesOutput:
    points = tuple(
        TimeSeriesPoint(timestamp=item.timestamp, value=item.value)
        for item in payload.observations
    )
    variable = EarthVariable(
        variable_id=request.variable_id,
        name=request.variable_name,
        description=request.description,
        category=request.category,
        metadata=VariableMetadata(
            unit=request.unit,
            temporal_resolutions=(request.temporal_resolution,),
        ),
    )
    series = TimeSeries(
        series_id=payload.region_id,
        variable=variable,
        location=SpatialCoordinate(
            latitude=payload.latitude,
            longitude=payload.longitude,
        ),
        temporal_resolution=request.temporal_resolution,
        points=points,
    )
    analysis: TrendAnalysisResult = analyzer.analyze(series)
    valid_points = [point for point in points if point.value is not None]

    average_interval_days: float | None = None
    linear_slope_per_period: float | None = None
    sen_slope_per_period: float | None = None
    net_change: float | None = None
    average: float | None = None

    if valid_points:
        average = fmean(float(point.value) for point in valid_points if point.value is not None)

    if len(valid_points) > 1:
        average_interval_days = (
            (valid_points[-1].timestamp - valid_points[0].timestamp).total_seconds()
            / 86400.0
            / (len(valid_points) - 1)
        )
        net_change = float(valid_points[-1].value) - float(valid_points[0].value)
        if analysis.linear_slope_per_day is not None:
            linear_slope_per_period = analysis.linear_slope_per_day * average_interval_days
        if analysis.sen_slope_per_day is not None:
            sen_slope_per_period = analysis.sen_slope_per_day * average_interval_days

    is_significant = (
        analysis.p_value < analysis.significance_level if analysis.p_value is not None else None
    )

    return TrendSeriesOutput(
        region_id=payload.region_id,
        direction=analysis.direction.value,
        strength=analysis.strength.value,
        input_observation_count=analysis.input_observation_count,
        valid_observation_count=analysis.valid_observation_count,
        missing_observation_count=analysis.missing_observation_count,
        linear_slope_per_day=analysis.linear_slope_per_day,
        linear_slope_per_period=linear_slope_per_period,
        sen_slope_per_day=analysis.sen_slope_per_day,
        sen_slope_per_period=sen_slope_per_period,
        average_interval_days=average_interval_days,
        net_change=net_change,
        average=average,
        r_squared=analysis.coefficient_of_determination,
        kendall_tau=analysis.kendall_tau,
        p_value=analysis.p_value,
        significance_level=analysis.significance_level,
        is_significant=is_significant,
        analyzed_at=analysis.analyzed_at,
    )


def _allowed_origins() -> list[str]:
    configured = os.environ.get("ETE_CORS_ORIGINS", "")
    if not configured.strip():
        return ["http://localhost:5173", "http://127.0.0.1:5173"]
    return [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]


app = FastAPI(title="Earth Twin Engine API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/v1/health", response_model=HealthOutput)
def health() -> HealthOutput:
    return HealthOutput(status="ok", model="TrendAnalyzer")


@app.post("/api/v1/trends/analyze", response_model=TrendBatchOutput)
def analyze_trends(request: TrendBatchInput) -> TrendBatchOutput:
    analyzer = TrendAnalyzer(significance_level=request.significance_level)
    try:
        results = [_analyze_series(item, request, analyzer) for item in request.series]
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    return TrendBatchOutput(
        model="TrendAnalyzer",
        method="ordinary_least_squares+sen_slope+mann_kendall",
        results=results,
    )
