import pytest
from axora.agent.decisions import AgentDecision, ToolCall
from axora.llm.provider import GroqLLMAdapter, MockLLMAdapter, NvidiaLLMAdapter, OpenAILLMAdapter, get_llm_adapter


@pytest.mark.asyncio
async def test_mock_llm_adapter_default_response():
    adapter = MockLLMAdapter()
    assert adapter.provider_name == "mock"
    assert adapter.model_name == "mock-agent-v1"

    decision = await adapter.decide("Bonjour, qui êtes-vous ?")
    assert isinstance(decision, AgentDecision)
    assert decision.type in ("call_tool", "final_answer")


@pytest.mark.asyncio
async def test_mock_llm_adapter_keyword_trigger():
    adapter = MockLLMAdapter()
    decision = await adapter.decide("Découvrir les entités du modèle")
    assert isinstance(decision, AgentDecision)
    assert decision.type == "call_tool"
    assert decision.tool_call.name == "discover_model"


@pytest.mark.asyncio
async def test_mock_llm_adapter_predefined_sequence():
    seq = [
        AgentDecision(
            type="call_tool",
            tool_call=ToolCall(name="discover_model", arguments={"concept": "Paroisse"}),
        ),
        AgentDecision(type="final_answer", content="Réponse finale simulée."),
    ]
    adapter = MockLLMAdapter(predefined_responses=seq)

    d1 = await adapter.decide("Etape 1")
    assert d1.type == "call_tool"
    assert d1.tool_call.arguments["concept"] == "Paroisse"

    d2 = await adapter.decide("Etape 2")
    assert d2.type == "final_answer"
    assert d2.content == "Réponse finale simulée."


@pytest.mark.asyncio
async def test_openai_llm_adapter_fallback():
    adapter = OpenAILLMAdapter(api_key="sk-proj-your-api-key-here", model="gpt-4o-mini")
    assert adapter.provider_name == "openai"
    assert adapter.model_name == "gpt-4o-mini"

    decision = await adapter.decide("Lister les membres")
    assert isinstance(decision, AgentDecision)
    assert decision.type in ("call_tool", "final_answer")


@pytest.mark.asyncio
async def test_nvidia_llm_adapter_fallback():
    adapter = NvidiaLLMAdapter(api_key="nvapi-your-key-here", model="meta/llama-3.1-70b-instruct")
    assert adapter.provider_name == "nvidia"
    assert adapter.model_name == "meta/llama-3.1-70b-instruct"

    decision = await adapter.decide("Qui sont les membres ?")
    assert isinstance(decision, AgentDecision)
    assert decision.type in ("call_tool", "final_answer")


@pytest.mark.asyncio
async def test_groq_llm_adapter_fallback():
    adapter = GroqLLMAdapter(api_key="gsk_your_free_groq_api_key_here", model="llama-3.3-70b-versatile")
    assert adapter.provider_name == "groq"
    assert adapter.model_name == "llama-3.3-70b-versatile"

    decision = await adapter.decide("Qui est Rakoto Jean ?")
    assert isinstance(decision, AgentDecision)
    assert decision.type in ("call_tool", "final_answer")


def test_get_llm_adapter_factory():
    mock_adapter = get_llm_adapter("mock")
    assert mock_adapter.provider_name == "mock"

    openai_adapter = get_llm_adapter("openai")
    assert openai_adapter.provider_name == "openai"

    nvidia_adapter = get_llm_adapter("nvidia")
    assert nvidia_adapter.provider_name == "nvidia"

    groq_adapter = get_llm_adapter("groq")
    assert groq_adapter.provider_name == "groq"
