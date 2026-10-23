from typing import Any, Literal, Protocol
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Standardized result wrapper returned by all generic tools."""

    status: Literal["success", "error"]
    data: Any = None
    error_code: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolInterface(Protocol):
    """Protocol that all Axora agent tools must implement."""

    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    @property
    def parameters_schema(self) -> dict[str, Any]:
        ...

    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        ...
