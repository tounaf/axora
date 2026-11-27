import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from axora.agent.decisions import AgentDecision, ToolCall
from axora.agent.loop import run_agent_loop
from axora.agent.runtime import AgentRuntime
from axora.cli import _display_progress
from axora.llm.provider import MockLLMAdapter
from axora.main import app
from axora.progress import ProgressCallback, ProgressEvent, publish_progress
from axora.semantic.service import SemanticModelService
from axora.tools.discover_model import DiscoverModelTool
from axora.tools.interface import ToolResult
from axora.tools.registry import ToolRegistry

YAML_PATH = Path("src/axora/semantic/definitions/gestion_paroissiale.yaml")


@pytest.fixture
def semantic_service():
    return SemanticModelService.from_yaml(YAML_PATH)


@pytest.fixture
def tool_registry(semantic_service):
    registry = ToolRegistry()
    registry.register(DiscoverModelTool(semantic_service))
    return registry


# ============================================================================
# 1. Tests unitaires du modèle d'événement et du dispatcher
# ============================================================================


def test_progress_event_model():
    now = datetime.now(timezone.utc)
    event = ProgressEvent(
        type="progress",
        phase="tool_execution",
        status="started",
        message="Recherche en cours…",
        tool="discover_model",
        iteration=1,
        max_iterations=5,
        timestamp=now,
    )
    assert event.type == "progress"
    assert event.phase == "tool_execution"
    assert event.status == "started"
    assert event.message == "Recherche en cours…"
    assert event.tool == "discover_model"
    assert event.iteration == 1
    assert event.max_iterations == 5
    assert event.timestamp == now

    dumped = event.model_dump(mode="json")
    assert dumped["type"] == "progress"
    assert dumped["phase"] == "tool_execution"
    assert "timestamp" in dumped


def test_publish_progress_with_callback():
    captured = []
    publish_progress(
        captured.append,
        phase="analysis",
        status="started",
        message="Analyse de l'intention…",
        iteration=1,
    )
    assert len(captured) == 1
    assert captured[0].phase == "analysis"
    assert captured[0].status == "started"
    assert captured[0].message == "Analyse de l'intention…"


def test_publish_progress_none_callback_noop():
    # Should not raise any error when callback is None
    publish_progress(
        None,
        phase="bootstrap",
        message="Ne rien faire.",
    )


# ============================================================================
# 2. Tests de progression dans la boucle agentique
# ============================================================================


@pytest.mark.asyncio
async def test_agent_loop_direct_final_answer_publishes_events(tool_registry):
    mock_llm = MockLLMAdapter([
        AgentDecision(type="final_answer", content="Réponse immédiate."),
    ])
    events: list[ProgressEvent] = []

    response = await run_agent_loop(
        "Bonjour",
        mock_llm,
        tool_registry,
        progress_callback=events.append,
    )

    assert response == "Réponse immédiate."
    assert len(events) == 2
    # 1. Analysis started
    assert events[0].phase == "analysis"
    assert events[0].status == "started"
    # 2. Response completed
    assert events[1].type == "completed"
    assert events[1].phase == "response"
    assert events[1].status == "completed"


@pytest.mark.asyncio
async def test_agent_loop_multi_tool_ordering_and_safety(tool_registry):
    mock_llm = MockLLMAdapter([
        AgentDecision(
            type="call_tool",
            tool_call=ToolCall(name="discover_model", arguments={"concept": "Membre"}),
        ),
        AgentDecision(type="final_answer", content="Voici la réponse après outil."),
    ])
    events: list[ProgressEvent] = []

    response = await run_agent_loop(
        "Décris l'entité Membre",
        mock_llm,
        tool_registry,
        progress_callback=events.append,
    )

    assert response == "Voici la réponse après outil."
    assert len(events) == 5
    assert [(e.phase, e.status) for e in events] == [
        ("analysis", "started"),
        ("tool_execution", "started"),
        ("tool_execution", "completed"),
        ("analysis", "started"),
        ("response", "completed"),
    ]
    # Verify tool name is present but sensitive arguments are not in the event
    assert events[1].tool == "discover_model"
    for e in events:
        json_str = e.model_dump_json()
        assert "concept" not in json_str
        assert "arguments" not in json_str


@pytest.mark.asyncio
async def test_agent_loop_tool_failure_marks_progress_failed(tool_registry):
    failing_tool = MagicMock()
    failing_tool.name = "failing_tool"
    failing_tool.execute = AsyncMock(side_effect=Exception("Database connection timeout"))
    tool_registry.register(failing_tool)

    mock_llm = MockLLMAdapter([
        AgentDecision(
            type="call_tool",
            tool_call=ToolCall(name="failing_tool", arguments={}),
        ),
        AgentDecision(type="final_answer", content="L'outil a échoué mais je réponds."),
    ])
    events: list[ProgressEvent] = []

    response = await run_agent_loop(
        "Appelle l'outil en panne",
        mock_llm,
        tool_registry,
        progress_callback=events.append,
    )

    assert response == "L'outil a échoué mais je réponds."
    tool_completed_event = events[2]
    assert tool_completed_event.phase == "tool_execution"
    assert tool_completed_event.status == "failed"
    assert "difficulté" in tool_completed_event.message


# ============================================================================
# 3. Tests de l'endpoint SSE /api/v1/chat/stream
# ============================================================================


def test_api_chat_stream_success():
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/stream",
        json={"message": "Bonjour via stream"},
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    lines = response.text.strip().split("\n\n")
    assert len(lines) >= 2

    parsed_events = []
    for frame in lines:
        event_type = None
        data = None
        for line in frame.split("\n"):
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                data = json.loads(line.split(":", 1)[1].strip())
        if event_type and data:
            parsed_events.append((event_type, data))

    # Should have intermediate progress events
    progress_types = [e[0] for e in parsed_events]
    assert "progress" in progress_types
    # Must end with completed event
    assert parsed_events[-1][0] == "completed"
    completed_payload = parsed_events[-1][1]
    assert "conversation_id" in completed_payload
    assert "response" in completed_payload
    assert completed_payload["status"] == "completed"


def test_api_chat_stream_error_handling():
    client = TestClient(app)
    with patch("axora.api.routes._process_chat_message", side_effect=RuntimeError("Erreur simulée")):
        response = client.post(
            "/api/v1/chat/stream",
            json={"message": "Provoquer une erreur"},
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        lines = response.text.strip().split("\n\n")
        parsed_events = []
        for frame in lines:
            event_type = None
            data = None
            for line in frame.split("\n"):
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                elif line.startswith("data:"):
                    data = json.loads(line.split(":", 1)[1].strip())
            if event_type and data:
                parsed_events.append((event_type, data))

        assert len(parsed_events) == 1
        assert parsed_events[0][0] == "error"
        assert "Une erreur est survenue" in parsed_events[0][1]["message"]


@pytest.mark.asyncio
async def test_concurrent_agent_loops_isolation(tool_registry):
    mock_llm1 = MockLLMAdapter([
        AgentDecision(type="final_answer", content="Réponse session 1"),
    ])
    mock_llm2 = MockLLMAdapter([
        AgentDecision(type="final_answer", content="Réponse session 2"),
    ])

    events1: list[ProgressEvent] = []
    events2: list[ProgressEvent] = []

    res1, res2 = await asyncio.gather(
        run_agent_loop("Msg 1", mock_llm1, tool_registry, progress_callback=events1.append),
        run_agent_loop("Msg 2", mock_llm2, tool_registry, progress_callback=events2.append),
    )

    assert res1 == "Réponse session 1"
    assert res2 == "Réponse session 2"
    assert len(events1) == 2
    assert len(events2) == 2
    assert events1[-1].type == "completed"
    assert events2[-1].type == "completed"


# ============================================================================
# 4. Tests d'affichage CLI
# ============================================================================


def test_cli_display_progress(capsys):
    event_ok = ProgressEvent(
        phase="analysis",
        status="started",
        message="Analyse en cours…",
    )
    _display_progress(event_ok)
    captured = capsys.readouterr()
    assert "[*] Analyse en cours…" in captured.out

    event_err = ProgressEvent(
        type="error",
        phase="installation",
        status="failed",
        message="Échec de l'installation.",
    )
    _display_progress(event_err)
    captured = capsys.readouterr()
    assert "[!] Échec de l'installation." in captured.out
