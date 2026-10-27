import logging
from typing import Any
from axora.data.query_engine import QueryEngine
from axora.semantic.service import SemanticModelService
from axora.tools.interface import ToolResult

logger = logging.getLogger("axora.tools.query_data")


class QueryDataTool:
    """Generic tool to safely query business data using abstract semantic filters."""

    def __init__(self, semantic_service: SemanticModelService, session_factory) -> None:
        self._semantic_service = semantic_service
        self._session_factory = session_factory
        self._query_engine = QueryEngine(semantic_service)

    @property
    def name(self) -> str:
        return "query_data"

    @property
    def description(self) -> str:
        return (
            "Query business data through structured semantic filters. Supports entity selection, "
            "field projections, relational filters (e.g. 'paroisse.nom', 'zone.nom') and limits."
        )

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entity": {
                    "type": "string",
                    "description": "Canonical entity or concept name to query (e.g. 'Membre', 'Paroisse').",
                },
                "select": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attributes/columns to retrieve.",
                },
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Field or relational path (e.g. 'nom', 'paroisse.nom', 'zone.nom')."},
                            "operator": {"type": "string", "enum": ["equals", "contains", "greater_than", "less_than"]},
                            "value": {"type": "string", "description": "Value to match against."},
                        },
                        "required": ["path", "operator", "value"],
                    },
                    "description": "List of filter conditions to apply.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of records to return (default: 50, max: 200).",
                    "default": 50,
                },
            },
            "required": ["entity"],
        }

    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        entity = arguments.get("entity")
        logger.info(f"[TOOL EXECUTING] query_data with arguments: {arguments}")

        if not entity:
            logger.error("[TOOL ERROR] query_data missing required 'entity' parameter.")
            return ToolResult(status="error", error_code="MISSING_ENTITY", message="The 'entity' parameter is required.")

        select_fields = arguments.get("select")
        filters = arguments.get("filters", [])
        limit = arguments.get("limit", 50)

        try:
            async with self._session_factory() as session:
                records = await self._query_engine.execute_query(
                    session=session,
                    entity_name=entity,
                    select_fields=select_fields,
                    filters=filters,
                    limit=limit,
                )
                logger.info(f"[TOOL SUCCESS] query_data retrieved {len(records)} records for entity '{entity}'.")
                return ToolResult(
                    status="success",
                    data={
                        "entity": entity,
                        "count": len(records),
                        "records": records,
                    },
                )
        except Exception as exc:
            logger.exception(f"[TOOL EXECUTION EXCEPTION] query_data failed for entity '{entity}': {exc}")
            return ToolResult(
                status="error",
                error_code="QUERY_EXECUTION_ERROR",
                message=f"Failed to execute query for entity '{entity}': {exc}",
            )
