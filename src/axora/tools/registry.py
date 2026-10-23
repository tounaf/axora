from typing import Any
from axora.tools.interface import ToolInterface


class ToolRegistry:
    """Central registry for discovering and dispatching generic agent tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolInterface] = {}

    def register(self, tool: ToolInterface) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolInterface:
        if name not in self._tools:
            raise ValueError(f"Unknown or unregistered tool: '{name}'.")
        return self._tools[name]

    def list_tools(self) -> list[ToolInterface]:
        return list(self._tools.values())

    def list_schemas(self) -> list[dict[str, Any]]:
        """Returns OpenAI/JSON-Schema compatible tool definitions for LLM prompts."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters_schema,
                },
            }
            for tool in self._tools.values()
        ]
