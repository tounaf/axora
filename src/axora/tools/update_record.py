from typing import Any
from axora.data.mutation_engine import BusinessRuleViolation, MutationEngine
from axora.semantic.service import SemanticModelService
from axora.tools.interface import ToolResult


class UpdateRecordTool:
    """Generic tool to update an existing business record with backend rule validation."""

    def __init__(self, semantic_service: SemanticModelService, session_factory) -> None:
        self._semantic_service = semantic_service
        self._session_factory = session_factory
        self._mutation_engine = MutationEngine(semantic_service)

    @property
    def name(self) -> str:
        return "update_record"

    @property
    def description(self) -> str:
        return (
            "Update an existing business record by its record_id. "
            "Validates domain business rules before saving."
        )

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entity": {
                    "type": "string",
                    "description": "Canonical entity name to update (e.g. 'Membre', 'Paroisse').",
                },
                "record_id": {
                    "type": "string",
                    "description": "UUID identifier of the record to update.",
                },
                "payload": {
                    "type": "object",
                    "description": "Dictionary of field attributes to modify.",
                },
            },
            "required": ["entity", "record_id", "payload"],
        }

    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        entity = arguments.get("entity")
        record_id = arguments.get("record_id")
        payload = arguments.get("payload")

        if not entity or not record_id or not payload:
            return ToolResult(
                status="error",
                error_code="INVALID_ARGUMENTS",
                message="'entity', 'record_id', and 'payload' parameters are required for update_record.",
            )

        try:
            async with self._session_factory() as session:
                async with session.begin():
                    record = await self._mutation_engine.update_record(
                        session=session,
                        entity_name=entity,
                        record_id=record_id,
                        payload=payload,
                    )
                return ToolResult(
                    status="success",
                    data={"entity": entity, "record": record},
                    message=f"Enregistrement '{record_id}' mis à jour avec succès dans '{entity}'.",
                )
        except BusinessRuleViolation as exc:
            return ToolResult(
                status="error",
                error_code="BUSINESS_RULE_VIOLATION",
                message=str(exc),
            )
        except Exception as exc:
            return ToolResult(
                status="error",
                error_code="UPDATE_EXECUTION_ERROR",
                message=f"Failed to update record '{record_id}' in '{entity}': {exc}",
            )
