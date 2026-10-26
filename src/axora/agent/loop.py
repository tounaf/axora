import logging
from typing import Any
from axora.agent.context import AgentContext
from axora.config import settings
from axora.llm.interface import LLMAdapter
from axora.tools.registry import ToolRegistry

logger = logging.getLogger("axora.agent.loop")


async def run_agent_loop(
    user_message: str,
    llm_adapter: LLMAdapter,
    tool_registry: ToolRegistry,
    history: list[dict[str, str]] | None = None,
    max_iterations: int | None = None,
) -> str:
    """Executes the bounded Agent loop.

    1. Builds context.
    2. Requests decision from LLM adapter.
    3. Validates decision type.
    4. Executes requested tool or returns final response.
    5. Repeats until final answer, clarification question, or iteration limit.
    """
    limit = max_iterations or settings.MAX_AGENT_ITERATIONS
    context = AgentContext(user_message=user_message, history=history or [])
    tools_schema = tool_registry.list_schemas()

    system_instruction = (
        "You are Axora Intent Agent. Your goal is to fulfill user intents by discovering domain "
        "semantics (`discover_model`) and querying data (`query_data`). Return structured decisions."
    )

    for iteration in range(1, limit + 1):
        prompt = context.build_prompt()
        logger.info(f"Agent Loop Iteration {iteration}/{limit}")

        decision = await llm_adapter.decide(
            prompt=prompt,
            tools_schema=tools_schema,
            system_instruction=system_instruction,
        )

        if decision.type == "final_answer":
            return decision.content or "Demande traitée."

        if decision.type == "ask_user":
            return decision.content or "Veuillez préciser votre demande."

        if decision.type == "call_tool" and decision.tool_call:
            tool_name = decision.tool_call.name
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

            context.append_observation(decision.tool_call, result)

    return (
        f"La demande n'a pas pu être finalisée dans la limite autorisée de {limit} itérations. "
        "Veuillez reformuler ou préciser votre besoin."
    )
