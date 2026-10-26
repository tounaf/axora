from typing import Any
from pydantic import BaseModel, Field
from axora.agent.decisions import ToolCall
from axora.tools.interface import ToolResult


class Observation(BaseModel):
    tool_call: ToolCall
    result: ToolResult


class AgentContext(BaseModel):
    user_message: str
    history: list[dict[str, str]] = Field(default_factory=list)
    observations: list[Observation] = Field(default_factory=list)

    def append_observation(self, tool_call: ToolCall, result: ToolResult) -> None:
        self.observations.append(Observation(tool_call=tool_call, result=result))

    def build_prompt(self) -> str:
        prompt_parts = []

        if self.history:
            prompt_parts.append("=== Conversation History ===")
            for msg in self.history:
                role = msg.get("role", "user").capitalize()
                content = msg.get("content", "")
                prompt_parts.append(f"{role}: {content}")
            prompt_parts.append("")

        prompt_parts.append("=== Current User Request ===")
        prompt_parts.append(self.user_message)

        if self.observations:
            prompt_parts.append("\n=== Tool Execution Observations ===")
            for idx, obs in enumerate(self.observations, 1):
                prompt_parts.append(
                    f"[{idx}] Tool: '{obs.tool_call.name}' | Args: {obs.tool_call.arguments}\n"
                    f"    Result Status: {obs.result.status}\n"
                    f"    Data/Payload: {obs.result.data}\n"
                    f"    Message: {obs.result.message or 'N/A'}"
                )

        return "\n".join(prompt_parts)
