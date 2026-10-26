import pytest
from pydantic import ValidationError
from axora.agent.decisions import AgentDecision, ToolCall


def test_valid_call_tool():
    decision = AgentDecision(
        type="call_tool",
        tool_call=ToolCall(name="discover_model", arguments={"concept": "Membre"}),
    )
    assert decision.type == "call_tool"
    assert decision.tool_call.name == "discover_model"


def test_invalid_call_tool_missing_payload():
    with pytest.raises(ValidationError):
        AgentDecision(type="call_tool")


def test_valid_final_answer():
    decision = AgentDecision(type="final_answer", content="Voici la réponse.")
    assert decision.type == "final_answer"
    assert decision.content == "Voici la réponse."


def test_invalid_final_answer_missing_content():
    with pytest.raises(ValidationError):
        AgentDecision(type="final_answer")
