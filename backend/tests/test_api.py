"""Integration tests for Flask API routes."""

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app("development")
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "mosquito-risk-api"


def test_risk_missing_city_name(client):
    response = client.post("/api/risk", json={})
    assert response.status_code == 400
    assert "city_name" in response.get_json()["error"]


def test_history_returns_empty_list(client):
    response = client.get("/api/history")
    assert response.status_code == 200
    assert response.get_json()["reports"] == []
