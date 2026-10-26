from pathlib import Path
import pytest
from axora.agent.decisions import AgentDecision, ToolCall
from axora.agent.loop import run_agent_loop
from axora.agent.runtime import AgentRuntime
from axora.llm.provider import MockLLMAdapter
from axora.semantic.service import SemanticModelService
from axora.tools.discover_model import DiscoverModelTool
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


@pytest.mark.asyncio
async def test_agent_loop_final_answer_direct(tool_registry):
    mock_llm = MockLLMAdapter([AgentDecision(type="final_answer", content="Bonjour, que souhaitez-vous savoir ?")])
    response = await run_agent_loop("Bonjour", mock_llm, tool_registry)
    assert response == "Bonjour, que souhaitez-vous savoir ?"


@pytest.mark.asyncio
async def test_agent_loop_ask_user(tool_registry):
    mock_llm = MockLLMAdapter([AgentDecision(type="ask_user", content="De quelle paroisse s'agit-il ?")])
    response = await run_agent_loop("Lister les membres", mock_llm, tool_registry)
    assert response == "De quelle paroisse s'agit-il ?"


@pytest.mark.asyncio
async def test_agent_loop_tool_call_then_final_answer(tool_registry):
    mock_llm = MockLLMAdapter([
        AgentDecision(type="call_tool", tool_call=ToolCall(name="discover_model", arguments={"concept": "Membre"})),
        AgentDecision(type="final_answer", content="J'ai analysé l'entité Membre. Elle contient nom, prenom, adresse."),
    ])
    response = await run_agent_loop("Décrire l'entité Membre", mock_llm, tool_registry)
    assert "J'ai analysé l'entité Membre" in response


@pytest.mark.asyncio
async def test_agent_loop_max_iterations_exceeded(tool_registry):
    # LLM keeps making tool calls indefinitely
    infinite_calls = [
        AgentDecision(type="call_tool", tool_call=ToolCall(name="discover_model", arguments={"concept": "Membre"}))
        for _ in range(10)
    ]
    mock_llm = MockLLMAdapter(infinite_calls)
    response = await run_agent_loop("Test boucle infinie", mock_llm, tool_registry, max_iterations=3)
    assert "n'a pas pu être finalisée" in response
    assert "3 itérations" in response


@pytest.mark.asyncio
async def test_agent_runtime_process_intent(tool_registry):
    mock_llm = MockLLMAdapter([AgentDecision(type="final_answer", content="Exécution réussie via Runtime.")])
    runtime = AgentRuntime(tool_registry=tool_registry, llm_adapter=mock_llm)

    response = await runtime.process_intent("Test Runtime")
    assert response == "Exécution réussie via Runtime."
