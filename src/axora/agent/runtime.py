from axora.agent.loop import run_agent_loop
from axora.llm.interface import LLMAdapter
from axora.llm.provider import get_llm_adapter
from axora.tools.registry import ToolRegistry


class AgentRuntime:
    """Core Agent Runtime orchestrating LLM adapter, tool registry, and execution loop."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        llm_adapter: LLMAdapter | None = None,
    ) -> None:
        self._tool_registry = tool_registry
        self._llm_adapter = llm_adapter or get_llm_adapter()

    @property
    def tool_registry(self) -> ToolRegistry:
        return self._tool_registry

    @property
    def llm_adapter(self) -> LLMAdapter:
        return self._llm_adapter

    async def process_intent(
        self,
        user_message: str,
        history: list[dict[str, str]] | None = None,
        max_iterations: int | None = None,
    ) -> str:
        """Processes a natural language intent through the agent execution loop."""
        return await run_agent_loop(
            user_message=user_message,
            llm_adapter=self._llm_adapter,
            tool_registry=self._tool_registry,
            history=history,
            max_iterations=max_iterations,
        )
