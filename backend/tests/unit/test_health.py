"""Smoke test for health endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_smoke() -> None:
    """Smoke test: verify /health returns HTTP 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "Dubai BizNavigator"


def test_api_v1_health_check() -> None:
    """Verify /api/v1/health returns HTTP 200 and status ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "Dubai BizNavigator"
