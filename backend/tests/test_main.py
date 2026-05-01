"""Tests d'intégration des endpoints FastAPI."""
import os
import sys

# Permet d'importer main.py situé un cran plus haut
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "devops-monitoring-backend"
    assert "endpoints" in body


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_metrics_endpoint_exposed():
    response = client.get("/metrics")
    assert response.status_code == 200
    # Format Prometheus text-based
    assert "http_requests_total" in response.text or "# HELP" in response.text


def test_sites_list():
    response = client.get("/sites")
    assert response.status_code == 200
    body = response.json()
    assert "sites" in body
    assert body["count"] == len(body["sites"])
    assert body["count"] > 0


def test_error_endpoint_returns_500():
    response = client.get("/error-test")
    assert response.status_code == 500
    assert "Erreur" in response.json()["detail"]
