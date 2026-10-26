import datetime
import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from axora.data.models import AdhesionAssociation, Association, Membre, Paroisse, ZoneGeographique
from axora.semantic.models import EntityDefinition
from axora.semantic.service import SemanticModelService

TABLE_TO_MODEL_MAP = {
    model_cls.__tablename__: model_cls
    for model_cls in (Paroisse, ZoneGeographique, Membre, Association, AdhesionAssociation)
}


class BusinessRuleViolation(Exception):
    """Raised when a data mutation violates a domain business rule derived from the semantic manifest."""
    pass


class MutationEngine:
    """Engine responsible for dynamically validating business rules and executing create/update mutations based on the Semantic Model Manifest."""

    def __init__(self, semantic_service: SemanticModelService) -> None:
        self._semantic_service = semantic_service

    async def create_record(
        self,
        session: AsyncSession,
        entity_name: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        entity_def = self._semantic_service.get_entity_details(entity_name)
        if not entity_def:
            raise ValueError(f"Unknown target entity or synonym: '{entity_name}'")

        table_name = entity_def.storage.table
        model_cls = TABLE_TO_MODEL_MAP.get(table_name)
        if not model_cls:
            raise ValueError(f"No ORM model mapped for storage table '{table_name}'")

        mapped_payload = self._map_and_convert_payload(entity_def, payload)
        await self._validate_semantic_rules(session, entity_def, mapped_payload)

        instance = model_cls(**mapped_payload)
        session.add(instance)
        await session.flush()

        return self._format_instance_output(instance, entity_def)

    async def update_record(
        self,
        session: AsyncSession,
        entity_name: str,
        record_id: str | uuid.UUID,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        entity_def = self._semantic_service.get_entity_details(entity_name)
        if not entity_def:
            raise ValueError(f"Unknown target entity or synonym: '{entity_name}'")

        table_name = entity_def.storage.table
        model_cls = TABLE_TO_MODEL_MAP.get(table_name)
        if not model_cls:
            raise ValueError(f"No ORM model mapped for storage table '{table_name}'")

        uid = uuid.UUID(str(record_id)) if isinstance(record_id, str) else record_id

        stmt = select(model_cls).where(getattr(model_cls, entity_def.storage.id) == uid)
        result = await session.execute(stmt)
        instance = result.scalar_one_or_none()

        if not instance:
            raise ValueError(f"Record with ID '{record_id}' not found in entity '{entity_name}'")

        mapped_payload = self._map_and_convert_payload(entity_def, payload)

        # Merge current instance state with update payload for full rule validation
        merged_payload = {
            col.name: getattr(instance, col.name)
            for col in instance.__table__.columns
        }
        merged_payload.update(mapped_payload)

        await self._validate_semantic_rules(session, entity_def, merged_payload)

        for col_name, val in mapped_payload.items():
            if hasattr(instance, col_name):
                setattr(instance, col_name, val)

        await session.flush()
        return self._format_instance_output(instance, entity_def)

    def _map_and_convert_payload(self, entity_def: EntityDefinition, payload: dict[str, Any]) -> dict[str, Any]:
        """Dynamically converts semantic attribute keys to database column names and casts data types according to the manifest."""
        mapped: dict[str, Any] = {}

        for key, val in payload.items():
            attr_def = entity_def.attributes.get(key)
            col_name = attr_def.column if attr_def else key

            if attr_def and attr_def.allowed_values and val not in attr_def.allowed_values:
                raise BusinessRuleViolation(
                    f"Valeur '{val}' non autorisée pour l'attribut '{key}'. Valeurs permises manifestes: {attr_def.allowed_values}"
                )

            if attr_def:
                if attr_def.type == "date" and isinstance(val, str):
                    val = datetime.date.fromisoformat(val)
                elif attr_def.type == "string" and key.endswith("_id") and isinstance(val, str):
                    val = uuid.UUID(val)

            if isinstance(val, str) and (col_name.endswith("_id") or col_name == "id"):
                try:
                    val = uuid.UUID(val)
                except ValueError:
                    pass

            mapped[col_name] = val

        return mapped

    async def _validate_semantic_rules(self, session: AsyncSession, entity_def: EntityDefinition, mapped_payload: dict[str, Any]) -> None:
        """Validates relational business constraints derived from semantic relationship metadata dynamically."""
        for rel_name, rel_def in entity_def.relationships.items():
            target_entity_def = self._semantic_service.get_entity_details(rel_def.target)
            if not target_entity_def:
                continue

            # Foreign key rule validation (e.g., ensuring child entity zone belongs to parent paroisse)
            fk_col = f"{rel_def.target.lower()}_id"
            if fk_col not in mapped_payload:
                fk_col = f"{target_entity_def.storage.table}_id"

            if fk_col in mapped_payload and rel_def.cardinality == "many-to-one":
                # Check for hierarchical zone-paroisse validation dynamically
                if entity_def.storage.table == "membre" and target_entity_def.storage.table == "zone_geographique":
                    zone_id = mapped_payload.get("zone_geographique_id")
                    paroisse_id = mapped_payload.get("paroisse_id")
                    if zone_id and paroisse_id:
                        zone_model = TABLE_TO_MODEL_MAP["zone_geographique"]
                        stmt = select(zone_model).where(
                            zone_model.id == zone_id,
                            zone_model.paroisse_id == paroisse_id
                        )
                        res = await session.execute(stmt)
                        if not res.scalar_one_or_none():
                            raise BusinessRuleViolation(
                                f"BR-001: La zone géographique '{zone_id}' n'appartient pas à la paroisse '{paroisse_id}' selon le manifeste."
                            )

    def _format_instance_output(self, instance: Any, entity_def: EntityDefinition) -> dict[str, Any]:
        """Formats an ORM instance output back into semantic attribute key names."""
        row_dict = {}
        for attr_key, attr_def in entity_def.attributes.items():
            col_name = attr_def.column
            if hasattr(instance, col_name):
                val = getattr(instance, col_name)
                row_dict[attr_key] = str(val) if isinstance(val, (uuid.UUID, datetime.date)) else val

        if hasattr(instance, entity_def.storage.id):
            id_val = getattr(instance, entity_def.storage.id)
            row_dict[entity_def.storage.id] = str(id_val) if isinstance(id_val, (uuid.UUID, datetime.date)) else id_val

        return row_dict
