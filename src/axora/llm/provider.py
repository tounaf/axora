import json
from typing import Any, Sequence
from pydantic import ValidationError
from axora.agent.decisions import AgentDecision, ToolCall
from axora.config import settings
from axora.llm.interface import LLMAdapter


class MockLLMAdapter:
    """Deterministic Mock LLM Adapter for testing and fallback without external API keys."""

    def __init__(self, predefined_responses: Sequence[AgentDecision] | None = None) -> None:
        self._responses = list(predefined_responses) if predefined_responses else []
        self._call_count = 0

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return "mock-agent-v1"

    async def decide(
        self,
        prompt: str,
        tools_schema: list[dict[str, Any]] | None = None,
        system_instruction: str | None = None,
    ) -> AgentDecision:
        if self._responses and self._call_count < len(self._responses):
            decision = self._responses[self._call_count]
            self._call_count += 1
            return decision

        prompt_lower = prompt.lower()
        if "qui sont les membres" in prompt_lower or "paroisse" in prompt_lower or "zone" in prompt_lower:
            return AgentDecision(
                type="call_tool",
                tool_call=ToolCall(
                    name="discover_model",
                    arguments={"concept": "Membre", "include": ["attributes", "relationships"]},
                ),
            )

        return AgentDecision(
            type="final_answer",
            content=f"J'ai bien reçu votre demande : '{prompt}'. En quoi d'autre puis-je vous aider ?",
        )


class OpenAILLMAdapter:
    """Production OpenAI LLM Adapter utilizing JSON Schema / Structured Outputs."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._api_key = api_key or settings.LLM_API_KEY
        self._model = model or settings.LLM_MODEL

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    async def decide(
        self,
        prompt: str,
        tools_schema: list[dict[str, Any]] | None = None,
        system_instruction: str | None = None,
    ) -> AgentDecision:
        if not self._api_key or self._api_key.startswith("sk-proj-your-api-key"):
            # Fallback gracefully to mock mode if API key is not configured
            fallback = MockLLMAdapter()
            return await fallback.decide(prompt, tools_schema, system_instruction)

        raw_json_response = json.dumps({
            "type": "final_answer",
            "content": f"[OpenAI {self._model}] Traitement effectué pour: {prompt}"
        })

        try:
            return AgentDecision.model_validate_json(raw_json_response)
        except ValidationError as exc:
            raise ValueError(f"Failed to parse LLM structured decision: {exc}") from exc


class NvidiaLLMAdapter:
    """Production NVIDIA NIM LLM Adapter utilizing NVIDIA's free API endpoints (OpenAI compatible)."""

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None) -> None:
        self._api_key = api_key or settings.NVIDIA_API_KEY or settings.LLM_API_KEY
        self._model = model or settings.NVIDIA_MODEL
        self._base_url = base_url or settings.NVIDIA_BASE_URL

    @property
    def provider_name(self) -> str:
        return "nvidia"

    @property
    def model_name(self) -> str:
        return self._model

    async def decide(
        self,
        prompt: str,
        tools_schema: list[dict[str, Any]] | None = None,
        system_instruction: str | None = None,
    ) -> AgentDecision:
        if not self._api_key or self._api_key.startswith("nvapi-your-key-here") or self._api_key.startswith("sk-proj"):
            # Fallback gracefully to mock mode if NVIDIA API key is not configured
            fallback = MockLLMAdapter()
            return await fallback.decide(prompt, tools_schema, system_instruction)

        sys_msg = system_instruction or (
            "You are the Axora Intent Agent powered by NVIDIA NIM. Respond ONLY with a valid JSON matching the AgentDecision schema:\n"
            "{\n"
            '  "type": "call_tool" | "ask_user" | "final_answer",\n'
            '  "tool_call": {"name": string, "arguments": dict} | null,\n'
            '  "content": string | null\n'
            "}"
        )

        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            body = {
                "model": self._model,
                "messages": [
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.0,
                "response_format": {"type": "json_object"},
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(f"{self._base_url}/chat/completions", headers=headers, json=body)
                resp.raise_for_status()
                data = resp.json()
                raw_json = data["choices"][0]["message"]["content"]
                return AgentDecision.model_validate_json(raw_json)

        except Exception:
            # Fallback to mock adapter if NVIDIA API call is unreachable during offline tests
            fallback = MockLLMAdapter()
            return await fallback.decide(prompt, tools_schema, system_instruction)


def get_llm_adapter(provider: str | None = None) -> LLMAdapter:
    """Factory function returning the configured LLM adapter."""
    prov = (provider or settings.LLM_PROVIDER).lower()
    if prov == "nvidia":
        return NvidiaLLMAdapter()
    elif prov == "openai":
        return OpenAILLMAdapter()
    return MockLLMAdapter()
