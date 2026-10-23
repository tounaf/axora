from typing import Any
from axora.semantic.service import SemanticModelService
from axora.tools.interface import ToolResult


class DiscoverModelTool:
    """Generic agent tool to inspect entities, attributes, relationships, and rules of the business domain."""

    def __init__(self, semantic_service: SemanticModelService) -> None:
        self._semantic_service = semantic_service

    @property
    def name(self) -> str:
        return "discover_model"

    @property
    def description(self) -> str:
        return (
            "Explore the semantic business model. Retrieve information about available entities, "
            "their attributes, relationships, synonyms, or business rules."
        )

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "concept": {
                    "type": "string",
                    "description": "Optional concept name or synonym to inspect (e.g. 'Membre', 'Paroisse', 'église'). If omitted, returns an overview of all concepts.",
                },
                "include": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["attributes", "relationships", "rules"],
                    },
                    "description": "Optional aspects to include in detail for a concept query.",
                },
            },
            "required": [],
        }

    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        concept = arguments.get("concept")
        include = arguments.get("include", ["attributes", "relationships"])

        # Case 1: No concept provided -> Return overview of all entities and rules
        if not concept:
            overview = self._semantic_service.get_entities_overview()
            rules = self._semantic_service.get_business_rules() if "rules" in include else []
            return ToolResult(
                status="success",
                data={
                    "model_name": self._semantic_service.model_name,
                    "version": self._semantic_service.version,
                    "entities": [item.model_dump() for item in overview],
                    "business_rules": [rule.model_dump() for rule in rules],
                },
            )

        # Case 2: Specific concept provided -> Resolve canonical entity definition
        entity_def = self._semantic_service.get_entity_details(concept)
        if not entity_def:
            return ToolResult(
                status="error",
                error_code="UNKNOWN_CONCEPT",
                message=f"Concept '{concept}' was not found in the semantic model.",
                data={"available_concepts": self._semantic_service.get_entity_names()},
            )

        canonical_name = self._semantic_service.resolve_concept_name(concept) or concept

        payload: dict[str, Any] = {
            "concept": canonical_name,
            "description": entity_def.description,
            "synonyms": entity_def.synonyms,
        }

        if "attributes" in include:
            payload["attributes"] = {
                attr_name: attr.model_dump()
                for attr_name, attr in entity_def.attributes.items()
            }

        if "relationships" in include:
            payload["relationships"] = {
                rel_name: rel.model_dump()
                for rel_name, rel in entity_def.relationships.items()
            }

        if "rules" in include:
            rules = self._semantic_service.get_business_rules()
            payload["rules"] = [rule.model_dump() for rule in rules]

        return ToolResult(
            status="success",
            data=payload,
            metadata={"query_concept": concept, "canonical_name": canonical_name},
        )
