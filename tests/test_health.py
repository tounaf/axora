import pytest
from fastapi.testclient import TestClient
from axora import main
from axora.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "axora"}


def test_readiness_check_when_database_is_available(monkeypatch):
    async def database_is_ready():
        return True

    monkeypatch.setattr(main, "_database_is_ready", database_is_ready)

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "axora",
        "database": "ready",
    }


def test_readiness_check_when_database_is_unavailable(monkeypatch):
    async def database_is_ready():
        return False

    monkeypatch.setattr(main, "_database_is_ready", database_is_ready)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["detail"] == {
        "status": "not_ready",
        "database": "unavailable",
    }


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "Axora"


def test_ui_dashboard_endpoint():
    response = client.get("/ui")
    assert response.status_code == 200
    assert "Axora" in response.text
