import logging
from typing import Any
from axora.agent.context import AgentContext
from axora.config import settings
from axora.llm.interface import LLMAdapter
from axora.progress import ProgressCallback, publish_progress
from axora.tools.registry import ToolRegistry

logger = logging.getLogger("axora.agent.loop")

_TOOL_PROGRESS_MESSAGES = {
    "discover_model": "Exploration du modèle métier en cours…",
    "query_data": "Recherche dans les données en cours…",
    "create_record": "Création de l'enregistrement en cours…",
    "update_record": "Mise à jour de l'enregistrement en cours…",
    "render_view": "Préparation de la visualisation en cours…",
}


async def run_agent_loop(
    user_message: str,
    llm_adapter: LLMAdapter,
    tool_registry: ToolRegistry,
    history: list[dict[str, str]] | None = None,
    max_iterations: int | None = None,
    context: AgentContext | None = None,
    progress_callback: ProgressCallback | None = None,
) -> str:
    """Executes the bounded Agent loop.

    1. Builds context.
    2. Requests decision from LLM adapter.
    3. Validates decision type.
    4. Executes requested tool or returns final response.
    5. Repeats until final answer, clarification question, or iteration limit.
    """
    limit = max_iterations or settings.MAX_AGENT_ITERATIONS
    if context is None:
        context = AgentContext(user_message=user_message, history=history or [])
    tools_schema = tool_registry.list_schemas()

    system_instruction = (
        "You are Axora Intent Agent. Your goal is to fulfill user intents by discovering domain "
        "semantics (`discover_model`) and querying data (`query_data`). Return structured decisions in valid JSON format matching the AgentDecision schema:\n"
        "{\n"
        "  \"type\": \"call_tool\" | \"ask_user\" | \"final_answer\",\n"
        "  \"tool_call\": {\"name\": string, \"arguments\": dict} | null,\n"
        "  \"content\": string | null\n"
        "}"
    )

    for iteration in range(1, limit + 1):
        prompt = context.build_prompt()
        logger.info(f"Agent Loop Iteration {iteration}/{limit}")
        publish_progress(
            progress_callback,
            phase="analysis",
            status="started",
            message=f"Analyse de la demande (étape {iteration}/{limit})…",
            iteration=iteration,
            max_iterations=limit,
        )

        decision = await llm_adapter.decide(
            prompt=prompt,
            tools_schema=tools_schema,
            system_instruction=system_instruction,
        )

        if decision.type == "final_answer":
            publish_progress(
                progress_callback,
                event_type="completed",
                phase="response",
                status="completed",
                message="Réponse prête.",
                iteration=iteration,
                max_iterations=limit,
            )
            return decision.content or "Demande traitée."

        if decision.type == "ask_user":
            publish_progress(
                progress_callback,
                event_type="completed",
                phase="clarification",
                status="completed",
                message="Une précision est nécessaire.",
                iteration=iteration,
                max_iterations=limit,
            )
            return decision.content or "Veuillez préciser votre demande."

        if decision.type == "call_tool" and decision.tool_call:
            tool_name = decision.tool_call.name
            tool_message = _TOOL_PROGRESS_MESSAGES.get(
                tool_name,
                "Exécution d'une action Axora en cours…",
            )
            publish_progress(
                progress_callback,
                phase="tool_execution",
                status="started",
                message=tool_message,
                tool=tool_name,
                iteration=iteration,
                max_iterations=limit,
            )
            try:
                tool = tool_registry.get(tool_name)
                result = await tool.execute(decision.tool_call.arguments)
            except Exception as exc:
                from axora.tools.interface import ToolResult
                result = ToolResult(
                    status="error",
                    error_code="TOOL_EXECUTION_EXCEPTION",
                    message=f"Failed to execute tool '{tool_name}': {exc}",
                )

            tool_succeeded = result.status == "success"
            publish_progress(
                progress_callback,
                phase="tool_execution",
                status="completed" if tool_succeeded else "failed",
                message=(
                    "Étape terminée."
                    if tool_succeeded
                    else "Cette étape a rencontré une difficulté ; Axora poursuit l'analyse."
                ),
                tool=tool_name,
                iteration=iteration,
                max_iterations=limit,
            )
            context.append_observation(decision.tool_call, result)

    limit_message = (
        f"La demande n'a pas pu être finalisée dans la limite autorisée de {limit} itérations. "
        "Veuillez reformuler ou préciser votre besoin."
    )
    publish_progress(
        progress_callback,
        event_type="error",
        phase="agent",
        status="failed",
        message=f"La limite de {limit} étapes a été atteinte.",
        max_iterations=limit,
    )
    return limit_message
