import pytest
from fastapi.testclient import TestClient
from axora.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "axora"}


def test_post_chat_message_new_conversation():
    payload = {"message": "Bonjour, qui êtes-vous ?"}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
    assert data["status"] == "completed"


def test_post_chat_message_and_retrieve_history():
    # 1. Post initial message
    post_res = client.post("/api/v1/chat", json={"message": "Lister les membres"})
    assert post_res.status_code == 200
    conv_id = post_res.json()["conversation_id"]

    # 2. Retrieve history for session
    get_res = client.get(f"/api/v1/conversations/{conv_id}")
    assert get_res.status_code == 200

    session_data = get_res.json()
    assert session_data["id"] == conv_id
    assert len(session_data["messages"]) == 2  # 1 user message + 1 assistant message
    assert session_data["messages"][0]["role"] == "user"
    assert session_data["messages"][1]["role"] == "assistant"
