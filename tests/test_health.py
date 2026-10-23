import pytest
from fastapi.testclient import TestClient
from axora.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "axora"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "Axora"
