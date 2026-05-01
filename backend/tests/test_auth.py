"""Tests d'authentification JWT."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)


def test_login_success():
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password():
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


def test_login_unknown_user():
    response = client.post(
        "/auth/login",
        json={"username": "ghost", "password": "anything"},
    )
    assert response.status_code == 401


def test_verify_token_valid():
    login_resp = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = login_resp.json()["access_token"]
    response = client.get(f"/auth/verify?token={token}")
    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["user"] == "admin"


def test_verify_token_invalid():
    response = client.get("/auth/verify?token=not.a.real.jwt")
    assert response.status_code == 401
