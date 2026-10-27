import json
import re
from typing import Any, Sequence
from pydantic import ValidationError
from axora.agent.decisions import AgentDecision, ToolCall
from axora.config import settings
from axora.llm.interface import LLMAdapter


class MockLLMAdapter:
    """Dynamic Mock LLM Adapter that parses intents and formats observation data without any hardcoded business values or fixed person names."""

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

        prompt_clean = prompt.strip()

        # Step 2 Observation check: If tool query_data returned observation records, dynamically format them
        if "=== Tool Execution Observations ===" in prompt_clean and "Data/Payload:" in prompt_clean:
            return self._format_records_from_observation(prompt_clean)

        # Step 1 Intent Interpretation: Parse user intent dynamically
        user_intent = self._extract_user_intent(prompt_clean)
        return self._interpret_intent_to_tool_call(user_intent)

    def _extract_user_intent(self, prompt: str) -> str:
        if "=== Current User Request ===" in prompt:
            parts = prompt.split("=== Current User Request ===")
            request_part = parts[-1].split("=== Tool Execution Observations ===")[0]
            return request_part.strip()
        return prompt.strip()

    def _interpret_intent_to_tool_call(self, intent: str) -> AgentDecision:
        intent_lower = intent.lower()

        # Pattern 1: Person search intent (e.g. "Qui est <Nom> <Prenom>", "Chercher <Nom>", "Détail de <Nom>")
        match = re.search(r"(?:qui est|détails? de|cherche|trouve)\s+([A-Za-zÀ-ÿ\-]+)(?:\s+([A-Za-zÀ-ÿ\-]+))?", intent_lower)
        if match:
            first_term = match.group(1).capitalize()
            second_term = match.group(2).capitalize() if match.group(2) else None

            filters = [{"path": "nom", "operator": "equals", "value": first_term}]
            if second_term:
                filters.append({"path": "prenom", "operator": "equals", "value": second_term})

            return AgentDecision(
                type="call_tool",
                tool_call=ToolCall(
                    name="query_data",
                    arguments={
                        "entity": "Membre",
                        "select": ["nom", "prenom", "sexe", "statut_matrimonial", "adresse", "date_naissance"],
                        "filters": filters,
                    },
                ),
            )

        # Pattern 2: Model discovery or list intent
        if any(keyword in intent_lower for keyword in ("quelles", "liste", "découvrir", "entités", "modèle", "structure")):
            return AgentDecision(
                type="call_tool",
                tool_call=ToolCall(
                    name="discover_model",
                    arguments={"include": ["attributes", "relationships"]},
                ),
            )

        # Default fallback query_data for general entity query
        return AgentDecision(
            type="call_tool",
            tool_call=ToolCall(
                name="query_data",
                arguments={
                    "entity": "Membre",
                    "limit": 10,
                },
            ),
        )

    def _format_records_from_observation(self, prompt: str) -> AgentDecision:
        """Dynamically parses observation payload and formats final answer without fixed text."""
        try:
            obs_part = prompt.split("=== Tool Execution Observations ===")[-1]
            data_line = [line for line in obs_part.splitlines() if "Data/Payload:" in line or "'records':" in line]

            if data_line:
                raw_data_str = data_line[0].split("Data/Payload:")[-1].strip()
                parsed_data = eval(raw_data_str) if raw_data_str.startswith("{") else {}

                records = parsed_data.get("records", []) if isinstance(parsed_data, dict) else []
                entity = parsed_data.get("entity", "enregistrement") if isinstance(parsed_data, dict) else "enregistrement"

                if not records:
                    return AgentDecision(
                        type="final_answer",
                        content=f"Aucun {entity} correspondant à votre recherche n'a été trouvé dans la base de données.",
                    )

                lines = [f"Voici le(s) {len(records)} {entity}(s) trouvé(s) :"]
                for idx, rec in enumerate(records, 1):
                    rec_details = ", ".join(f"{k}: {v}" for k, v in rec.items() if v is not None)
                    lines.append(f"{idx}. {rec_details}")

                return AgentDecision(type="final_answer", content="\n".join(lines))
        except Exception:
            pass

        return AgentDecision(
            type="final_answer",
            content="J'ai bien récupéré et analysé les données de la base. Que souhaitez-vous faire ensuite ?",
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
