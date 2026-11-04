from typing import Any
from axora.tools.interface import ToolResult
from axora.views.registry import ViewRegistry


class RenderViewTool:
    """Generic tool allowing the agent or UI to construct an interactive view payload (table, chart, metrics)."""

    def __init__(self, view_registry: ViewRegistry) -> None:
        self._view_registry = view_registry

    @property
    def name(self) -> str:
        return "render_view"

    @property
    def description(self) -> str:
        types = self._view_registry.list_types()
        return (
            f"Formats business data into a rich interactive UI component. "
            f"Supported view_types: {types}. For tables, provide records; for charts, provide series."
        )

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "view_type": {
                    "type": "string",
                    "description": f"Target view type ({', '.join(self._view_registry.list_types())})",
                },
                "title": {
                    "type": "string",
                    "description": "Descriptive title for the view component",
                },
                "data": {
                    "type": "object",
                    "description": "Payload containing records, series, or metric cards",
                },
            },
            "required": ["view_type", "data"],
        }

    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        view_type = arguments.get("view_type", "table")
        title = arguments.get("title", "")
        data = arguments.get("data", {})

        if not self._view_registry.has(view_type):
            return ToolResult(
                status="error",
                error_code="UNSUPPORTED_VIEW_TYPE",
                message=f"View type '{view_type}' is not registered. Available: {self._view_registry.list_types()}",
            )

        try:
            view_payload = self._view_registry.build_view(view_type, data, title=title)
            return ToolResult(
                status="success",
                data=view_payload.model_dump(),
                message=f"View '{view_type}' generated successfully.",
            )
        except Exception as exc:
            return ToolResult(
                status="error",
                error_code="VIEW_BUILDER_ERROR",
                message=f"Failed to build view '{view_type}': {exc}",
            )
