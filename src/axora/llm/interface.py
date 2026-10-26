from typing import Any, Protocol
from axora.agent.decisions import AgentDecision


class LLMAdapter(Protocol):
    """Protocol defining the interface for all LLM provider adapters in Axora."""

    @property
    def provider_name(self) -> str:
        """Returns the name of the LLM provider (e.g. 'openai', 'anthropic', 'mock')."""
        ...

    @property
    def model_name(self) -> str:
        """Returns the underlying model identifier (e.g. 'gpt-4o-mini', 'claude-3-5-sonnet')."""
        ...

    async def decide(
        self,
        prompt: str,
        tools_schema: list[dict[str, Any]] | None = None,
        system_instruction: str | None = None,
    ) -> AgentDecision:
        """Asynchronously calls the LLM provider and parses the response into a validated AgentDecision.

        Raises ValueError or ValidationError if the response cannot be parsed into a valid AgentDecision.
        """
        ...
