import datetime
import uuid
from typing import Any
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from axora.data.dynamic_models import get_dynamic_table
from axora.semantic.models import EntityDefinition
from axora.semantic.service import SemanticModelService


class BusinessRuleViolation(Exception):
    """Raised when a data mutation violates a domain business rule derived from the semantic manifest."""
    pass


class MutationEngine:
    """Engine responsible for dynamically validating business rules and executing create/update mutations based strictly on the Semantic Model Manifest without hardcoded entity or column names."""

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
        table_obj = get_dynamic_table(table_name, self._semantic_service)

        mapped_payload = self._map_and_convert_payload(entity_def, payload)

        # Auto-generate Primary Key UUID if not supplied
        pk_col = entity_def.storage.id
        if pk_col in table_obj.c and pk_col not in mapped_payload:
            mapped_payload[pk_col] = uuid.uuid4()

        await self._validate_semantic_rules(session, entity_def, mapped_payload)

        stmt = insert(table_obj).values(**mapped_payload)
        await session.execute(stmt)
        await session.flush()

        return self._format_dict_output(mapped_payload, entity_def)

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
        table_obj = get_dynamic_table(table_name, self._semantic_service)

        uid = uuid.UUID(str(record_id)) if isinstance(record_id, str) else record_id
        pk_col = entity_def.storage.id

        # Verify record existence
        select_stmt = select(table_obj).where(table_obj.c[pk_col] == uid)
        existing_res = await session.execute(select_stmt)
        existing_row = existing_res.fetchone()

        if not existing_row:
            raise ValueError(f"Record with ID '{record_id}' not found in entity '{entity_name}'")

        mapped_payload = self._map_and_convert_payload(entity_def, payload)

        # Merge existing record state with update payload for full rule validation
        merged_payload = dict(existing_row._mapping)
        merged_payload.update(mapped_payload)

        await self._validate_semantic_rules(session, entity_def, merged_payload)

        update_stmt = update(table_obj).where(table_obj.c[pk_col] == uid).values(**mapped_payload)
        await session.execute(update_stmt)
        await session.flush()

        return self._format_dict_output(merged_payload, entity_def)

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

            if isinstance(val, str) and (col_name.endswith("_id") or col_name == entity_def.storage.id):
                try:
                    val = uuid.UUID(val)
                except ValueError:
                    pass

            mapped[col_name] = val

        return mapped

    async def _validate_semantic_rules(self, session: AsyncSession, entity_def: EntityDefinition, mapped_payload: dict[str, Any]) -> None:
        """Validates relational business constraints derived 100% dynamically from semantic relationship metadata."""
        for rel_name, rel_def in entity_def.relationships.items():
            if rel_def.cardinality != "many-to-one":
                continue

            target_entity_def = self._semantic_service.get_entity_details(rel_def.target)
            if not target_entity_def:
                continue

            # Determine column names dynamically from relationship definition and target entity storage
            target_table_name = target_entity_def.storage.table
            fk_col_direct = f"{target_table_name}_id"
            fk_col_rel = f"{rel_name}_id"

            fk_col = fk_col_direct if fk_col_direct in mapped_payload else (fk_col_rel if fk_col_rel in mapped_payload else None)
            if not fk_col:
                continue

            target_fk_val = mapped_payload.get(fk_col)
            if not target_fk_val:
                continue

            # Inspect secondary relationships of the target entity to verify hierarchical parent/child integrity
            for target_rel_name, target_rel_def in target_entity_def.relationships.items():
                if target_rel_def.cardinality != "many-to-one":
                    continue

                parent_entity_def = self._semantic_service.get_entity_details(target_rel_def.target)
                if not parent_entity_def:
                    continue

                parent_table_name = parent_entity_def.storage.table
                parent_fk_col = f"{parent_table_name}_id"

                if parent_fk_col in mapped_payload:
                    expected_parent_val = mapped_payload[parent_fk_col]

                    # Verify target entity row in database matches the expected parent FK
                    target_table_obj = get_dynamic_table(target_table_name, self._semantic_service)
                    stmt = select(target_table_obj).where(
                        target_table_obj.c[target_entity_def.storage.id] == target_fk_val,
                        target_table_obj.c[parent_fk_col] == expected_parent_val
                    )
                    res = await session.execute(stmt)
                    if not res.fetchone():
                        raise BusinessRuleViolation(
                            f"BR-001: L'enregistrement '{target_entity_def.storage.table}' ({target_fk_val}) "
                            f"n'est pas rattaché à l'entité parente '{parent_entity_def.storage.table}' ({expected_parent_val}) selon le manifeste."
                        )

    def _format_dict_output(self, row_dict: dict[str, Any], entity_def: EntityDefinition) -> dict[str, Any]:
        """Formats a database mapping row output back into semantic attribute key names."""
        output = {}
        for attr_key, attr_def in entity_def.attributes.items():
            col_name = attr_def.column
            if col_name in row_dict:
                val = row_dict[col_name]
                output[attr_key] = str(val) if isinstance(val, (uuid.UUID, datetime.date)) else val

        pk_col = entity_def.storage.id
        if pk_col in row_dict:
            val = row_dict[pk_col]
            output[pk_col] = str(val) if isinstance(val, (uuid.UUID, datetime.date)) else val

        return output
