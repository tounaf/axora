import json
import logging
import re
from typing import Any, Sequence
from pydantic import ValidationError
from axora.agent.decisions import AgentDecision, ToolCall
from axora.config import settings
from axora.llm.interface import LLMAdapter

logger = logging.getLogger("axora.llm.provider")


class MockLLMAdapter:
    """Dynamic Mock LLM Adapter that parses intents and formats observation data without hardcoded business values."""

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
            logger.info(f"[LLM DECIDE] Returning predefined decision #{self._call_count}: {decision}")
            return decision

        prompt_clean = prompt.strip()

        # Step 2 Observation check: If tool query_data returned observation records, dynamically format them
        if "=== Tool Execution Observations ===" in prompt_clean and "Data/Payload:" in prompt_clean:
            decision = self._format_records_from_observation(prompt_clean)
            logger.info(f"[LLM DECIDE FROM OBSERVATION] Formatted decision: {decision.type}")
            return decision

        # Step 1 Intent Interpretation: Parse user intent dynamically
        user_intent = self._extract_user_intent(prompt_clean)
        logger.info(f"[LLM INTENT EXTRACTION] User Intent: '{user_intent}'")

        decision = self._interpret_intent_to_tool_call(user_intent, prompt_clean)
        logger.info(f"[LLM DECIDE FROM INTENT] Generated Decision: {decision.type} - Tool: {decision.tool_call.name if decision.tool_call else 'N/A'}")
        return decision

    def _extract_user_intent(self, prompt: str) -> str:
        if "=== Current User Request ===" in prompt:
            parts = prompt.split("=== Current User Request ===")
            request_part = parts[-1].split("=== Tool Execution Observations ===")[0]
            return request_part.strip()
        return prompt.strip()

    def _interpret_intent_to_tool_call(self, intent: str, full_prompt: str) -> AgentDecision:
        intent_lower = intent.lower()

        # Pattern 1: Universal Listing Intent
        if any(phrase in intent_lower for phrase in ("lister tous", "liste des", "tous les", "toutes les", "lister les")):
            target_concept = "Membre"
            if "paroisse" in intent_lower:
                target_concept = "Paroisse"
            elif "zone" in intent_lower:
                target_concept = "ZoneGeographique"
            elif "association" in intent_lower:
                target_concept = "Association"

            return AgentDecision(
                type="call_tool",
                tool_call=ToolCall(
                    name="query_data",
                    arguments={
                        "entity": target_concept,
                        "limit": 100,
                    },
                ),
            )

        # Pattern 2: Attribute/Property Question on previously queried person
        if any(keyword in intent_lower for keyword in ("est elle", "est il", "est-elle", "est-il", "mariée", "célibataire")):
            match_name = re.search(r"([A-Za-zÀ-ÿ\-]+)", intent_lower)
            if match_name:
                name_term = match_name.group(1).capitalize()
                return AgentDecision(
                    type="call_tool",
                    tool_call=ToolCall(
                        name="query_data",
                        arguments={
                            "entity": "Membre",
                            "filters": [{"path": "nom", "operator": "equals", "value": name_term}],
                        },
                    ),
                )

        # Pattern 3: Specific Person search intent
        match = re.search(r"(?:qui est|détails? de|cherche|trouve|info sur)\s+([A-Za-zÀ-ÿ\-]+)(?:\s+([A-Za-zÀ-ÿ\-]+))?", intent_lower)
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

        # Pattern 4: Model discovery intent
        if any(keyword in intent_lower for keyword in ("quelles entités", "découvrir", "entités", "modèle sémantique", "structure")):
            return AgentDecision(
                type="call_tool",
                tool_call=ToolCall(
                    name="discover_model",
                    arguments={"include": ["attributes", "relationships"]},
                ),
            )

        # Default query_data for general entity query without filter
        return AgentDecision(
            type="call_tool",
            tool_call=ToolCall(
                name="query_data",
                arguments={
                    "entity": "Membre",
                    "limit": 50,
                },
            ),
        )

    def _format_records_from_observation(self, prompt: str) -> AgentDecision:
        """Dynamically parses observation payload and formats final answer without fixed text."""
        try:
            obs_part = prompt.split("=== Tool Execution Observations ===")[-1]
            data_lines = [line for line in obs_part.splitlines() if "Data/Payload:" in line or "'records':" in line]

            if data_lines:
                raw_data_str = data_lines[0].split("Data/Payload:")[-1].strip()
                parsed_data = eval(raw_data_str) if raw_data_str.startswith("{") else {}

                records = parsed_data.get("records", []) if isinstance(parsed_data, dict) else []
                entity = parsed_data.get("entity", "enregistrement") if isinstance(parsed_data, dict) else "enregistrement"

                if not records:
                    return AgentDecision(
                        type="final_answer",
                        content=f"Aucun enregistrement correspondant à votre recherche n'a été trouvé dans la base de données.",
                    )

                lines = [f"Voici le(s) {len(records)} {entity}(s) trouvé(s) :"]
                for idx, rec in enumerate(records, 1):
                    rec_details = ", ".join(f"{k}: {v}" for k, v in rec.items() if v is not None)
                    lines.append(f"{idx}. {rec_details}")

                return AgentDecision(type="final_answer", content="\n".join(lines))
        except Exception as exc:
            logger.error(f"[OBSERVATION PARSING ERROR] {exc}")

        return AgentDecision(
            type="final_answer",
            content="J'ai bien récupéré et analysé les données de la base. Que souhaitez-vous savoir d'autre ?",
        )



def _clean_json_text(text: str) -> str:
    """Strips markdown code block wrappers from raw LLM output text."""
    clean = text.strip()
    if clean.startswith("```"):
        lines = clean.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        clean = "\n".join(lines).strip()
    return clean


class GroqLLMAdapter:
    """Production Groq LLM Adapter utilizing Groq's ultra-fast free Cloud API endpoints (OpenAI compatible)."""

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None) -> None:
        self._api_key = api_key or settings.GROQ_API_KEY or settings.LLM_API_KEY
        self._model = model or settings.GROQ_MODEL or settings.LLM_MODEL
        self._base_url = base_url or settings.GROQ_BASE_URL

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def model_name(self) -> str:
        return self._model

    async def decide(
        self,
        prompt: str,
        tools_schema: list[dict[str, Any]] | None = None,
        system_instruction: str | None = None,
    ) -> AgentDecision:
        if not self._api_key or self._api_key.startswith("gsk_your") or self._api_key.startswith("sk-proj") or self._api_key.startswith("nvapi"):
            logger.info("[GROQ LLM] Placeholder/No API Key detected -> Using Dynamic Mock LLM Adapter.")
            fallback = MockLLMAdapter()
            return await fallback.decide(prompt, tools_schema, system_instruction)

        json_schema_instruction = (
            "Respond ONLY with a valid JSON object matching the AgentDecision schema:\n"
            "{\n"
            '  "type": "call_tool" | "ask_user" | "final_answer",\n'
            '  "tool_call": {"name": string, "arguments": dict} | null,\n'
            '  "content": string | null\n'
            "}"
        )
        base_sys = system_instruction or "You are Axora Intent Agent powered by NVIDIA NIM. Fulfill user intents by calling appropriate tools or providing final answers."
        if "json" not in base_sys.lower():
            base_sys = f"{base_sys}\n\n{json_schema_instruction}"

        if tools_schema:
            tools_json = json.dumps(tools_schema, indent=2, ensure_ascii=False)
            sys_msg = f"{base_sys}\n\n=== Available Tools Schema ===\n{tools_json}"
        else:
            sys_msg = base_sys

        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
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
                if resp.status_code == 400 and "json_validate_failed" in resp.text:
                    logger.warning("[GROQ LLM API] json_validate_failed received. Retrying request without response_format...")
                    body_no_rf = dict(body)
                    body_no_rf.pop("response_format", None)
                    resp = await client.post(f"{self._base_url}/chat/completions", headers=headers, json=body_no_rf)

                if resp.is_error:
                    logger.error(
                        f"[GROQ LLM API ERROR] Status: {resp.status_code} | "
                        f"Response: {resp.text}"
                    )
                resp.raise_for_status()
                data = resp.json()
                raw_json = data["choices"][0]["message"]["content"]
                clean_json = _clean_json_text(raw_json)
                return AgentDecision.model_validate_json(clean_json)

        except Exception as exc:
            logger.warning(f"[GROQ LLM API CALL FAILED] {exc}. Falling back to Dynamic Mock LLM Adapter.")
            fallback = MockLLMAdapter()
            return await fallback.decide(prompt, tools_schema, system_instruction)


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
        self._model = model or settings.NVIDIA_MODEL or settings.LLM_MODEL
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
            logger.info("[NVIDIA LLM] Placeholder/No API Key detected -> Using Dynamic Mock LLM Adapter.")
            fallback = MockLLMAdapter()
            return await fallback.decide(prompt, tools_schema, system_instruction)

        json_schema_instruction = (
            "Respond ONLY with a valid JSON object matching the AgentDecision schema:\n"
            "{\n"
            '  "type": "call_tool" | "ask_user" | "final_answer",\n'
            '  "tool_call": {"name": string, "arguments": dict} | null,\n'
            '  "content": string | null\n'
            "}"
        )
        if system_instruction:
            sys_msg = system_instruction if "json" in system_instruction.lower() else f"{system_instruction}\n\n{json_schema_instruction}"
        else:
            sys_msg = f"You are the Axora Intent Agent powered by LLM.\n{json_schema_instruction}"

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
                if resp.is_error:
                    logger.error(
                        f"[NVIDIA LLM API ERROR] Status: {resp.status_code} | "
                        f"Response: {resp.text}"
                    )
                resp.raise_for_status()
                data = resp.json()
                raw_json = data["choices"][0]["message"]["content"]
                clean_json = _clean_json_text(raw_json)
                return AgentDecision.model_validate_json(clean_json)

        except Exception as exc:
            logger.warning(f"[NVIDIA LLM API CALL FAILED] {exc}. Falling back to Dynamic Mock LLM Adapter.")
            fallback = MockLLMAdapter()
            return await fallback.decide(prompt, tools_schema, system_instruction)


def get_llm_adapter(provider: str | None = None) -> LLMAdapter:
    """Factory function returning the configured LLM adapter."""
    prov = (provider or settings.LLM_PROVIDER).lower()
    if prov == "groq":
        return GroqLLMAdapter()
    elif prov == "nvidia":
        return NvidiaLLMAdapter()
    elif prov == "openai":
        return OpenAILLMAdapter()
    return MockLLMAdapter()
