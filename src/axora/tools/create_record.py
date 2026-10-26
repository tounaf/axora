from typing import Any
from axora.data.mutation_engine import BusinessRuleViolation, MutationEngine
from axora.semantic.service import SemanticModelService
from axora.tools.interface import ToolResult


class CreateRecordTool:
    """Generic tool to create a new business record with backend rule validation."""

    def __init__(self, semantic_service: SemanticModelService, session_factory) -> None:
        self._semantic_service = semantic_service
        self._session_factory = session_factory
        self._mutation_engine = MutationEngine(semantic_service)

    @property
    def name(self) -> str:
        return "create_record"

    @property
    def description(self) -> str:
        return (
            "Create a new business record (e.g. 'Membre', 'Paroisse', 'ZoneGeographique'). "
            "Validates domain business rules before saving."
        )

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entity": {
                    "type": "string",
                    "description": "Canonical entity name to create (e.g. 'Membre', 'Paroisse').",
                },
                "payload": {
                    "type": "object",
                    "description": "Dictionary of field attribute key-value pairs for the new record.",
                },
            },
            "required": ["entity", "payload"],
        }

    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        entity = arguments.get("entity")
        payload = arguments.get("payload")

        if not entity or not payload:
            return ToolResult(
                status="error",
                error_code="INVALID_ARGUMENTS",
                message="Both 'entity' and 'payload' parameters are required for create_record.",
            )

        try:
            async with self._session_factory() as session:
                async with session.begin():
                    record = await self._mutation_engine.create_record(
                        session=session,
                        entity_name=entity,
                        payload=payload,
                    )
                return ToolResult(
                    status="success",
                    data={"entity": entity, "record": record},
                    message=f"Enregistrement créé avec succès dans '{entity}'.",
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
                error_code="CREATE_EXECUTION_ERROR",
                message=f"Failed to create record in '{entity}': {exc}",
            )
