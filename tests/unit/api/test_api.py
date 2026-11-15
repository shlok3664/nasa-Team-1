"""Tests for the HTTP API and its connection to the trend model."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from earth_twin_engine.api import app

client = TestClient(app)


def create_request(values: list[float | None]) -> dict[str, Any]:
    return {
        "variable_id": "surface_temperature",
        "variable_name": "Surface temperature",
        "description": "Simulated monthly surface temperature.",
        "unit": "degC",
        "category": "atmosphere",
        "temporal_resolution": "monthly",
        "significance_level": 0.05,
        "series": [
            {
                "region_id": "amazon_basin",
                "latitude": -3.4,
                "longitude": -62.2,
                "observations": [
                    {
                        "timestamp": f"2025-{month:02d}-15T00:00:00Z",
                        "value": value,
                    }
                    for month, value in enumerate(values, start=1)
                ],
            }
        ],
    }


def test_health_reports_the_available_statistical_model() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model": "TrendAnalyzer"}


def test_analysis_endpoint_runs_existing_trend_model() -> None:
    response = client.post(
        "/api/v1/trends/analyze",
        json=create_request([10.0, 12.0, 14.0, 16.0, 18.0, 20.0]),
    )

    assert response.status_code == 200
    payload = response.json()
    result = payload["results"][0]
    assert payload["model"] == "TrendAnalyzer"
    assert result["direction"] == "increasing"
    assert result["strength"] == "very_strong"
    assert result["linear_slope_per_period"] == pytest.approx(2.0, abs=0.02)
    assert result["sen_slope_per_period"] == pytest.approx(2.0, abs=0.02)
    assert result["p_value"] < result["significance_level"]
    assert result["is_significant"] is True


def test_analysis_endpoint_rejects_non_increasing_timestamps() -> None:
    payload = create_request([10.0, 12.0, 14.0])
    observations = payload["series"][0]["observations"]
    observations[1]["timestamp"] = observations[0]["timestamp"]

    response = client.post("/api/v1/trends/analyze", json=payload)

    assert response.status_code == 422
    assert "strictly increasing" in response.json()["detail"]
