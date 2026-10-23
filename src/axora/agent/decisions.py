from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentDecision(BaseModel):
    """Structured decision contract returned by the LLM adapter."""

    type: Literal["call_tool", "ask_user", "final_answer"]
    tool_call: ToolCall | None = None
    content: str | None = None

    @model_validator(mode="after")
    def validate_decision_structure(self) -> "AgentDecision":
        if self.type == "call_tool" and not self.tool_call:
            raise ValueError("Type 'call_tool' requires a 'tool_call' payload.")
        if self.type in ("ask_user", "final_answer") and not self.content:
            raise ValueError(f"Type '{self.type}' requires 'content' text.")
        return self
