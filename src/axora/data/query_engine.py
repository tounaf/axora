import logging
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from axora.data.dynamic_models import get_dynamic_table
from axora.semantic.models import EntityDefinition
from axora.semantic.service import SemanticModelService

logger = logging.getLogger("axora.data.query_engine")


class QueryEngine:
    """Translates structured semantic queries into safe, parameterized SQLAlchemy async queries dynamically from the semantic model without static ORM classes."""

    def __init__(self, semantic_service: SemanticModelService) -> None:
        self._semantic_service = semantic_service

    async def execute_query(
        self,
        session: AsyncSession,
        entity_name: str,
        select_fields: list[str] | None = None,
        filters: list[dict[str, Any]] | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        entity_def = self._semantic_service.get_entity_details(entity_name)
        if not entity_def:
            logger.error(f"[QUERY ENGINE] Unknown entity name: '{entity_name}'")
            raise ValueError(f"Unknown target entity or synonym: '{entity_name}'")

        table_name = entity_def.storage.table
        primary_table = get_dynamic_table(table_name, self._semantic_service)

        stmt = select(primary_table)
        joined_tables = set()
        filters = filters or []

        logger.info(f"[QUERY ENGINE] Building SQL select for entity '{entity_name}' (table '{table_name}') with {len(filters)} filters.")

        for flt in filters:
            path = flt.get("path")
            operator = flt.get("operator", "equals")
            value = flt.get("value")

            if not path:
                continue

            parts = path.split(".")
            if len(parts) == 1:
                attr_name = parts[0]
                attr_def = entity_def.attributes.get(attr_name)
                col_name = attr_def.column if attr_def else attr_name
                if col_name in primary_table.c:
                    column = primary_table.c[col_name]
                    stmt = self._apply_filter(stmt, column, operator, value)
                    logger.info(f"[QUERY ENGINE] Applied direct filter: {col_name} {operator} '{value}'")

            elif len(parts) == 2:
                rel_name, target_attr = parts[0], parts[1]
                rel_def = entity_def.relationships.get(rel_name)

                if rel_def:
                    target_entity_def = self._semantic_service.get_entity_details(rel_def.target)
                    if target_entity_def:
                        target_table_name = target_entity_def.storage.table
                        target_table = get_dynamic_table(target_table_name, self._semantic_service)

                        if target_table_name not in joined_tables and target_table_name != table_name:
                            fk_col_name = f"{target_table_name}_id"
                            if fk_col_name in primary_table.c and target_entity_def.storage.id in target_table.c:
                                stmt = stmt.join(
                                    target_table,
                                    primary_table.c[fk_col_name] == target_table.c[target_entity_def.storage.id]
                                )
                            elif entity_def.storage.id in primary_table.c and f"{table_name}_id" in target_table.c:
                                stmt = stmt.join(
                                    target_table,
                                    primary_table.c[entity_def.storage.id] == target_table.c[f"{table_name}_id"]
                                )
                            else:
                                stmt = stmt.join(target_table)

                            joined_tables.add(target_table_name)
                            logger.info(f"[QUERY ENGINE] Joined table '{target_table_name}' via relationship '{rel_name}'")

                        target_attr_def = target_entity_def.attributes.get(target_attr)
                        col_name = target_attr_def.column if target_attr_def else target_attr
                        if col_name in target_table.c:
                            column = target_table.c[col_name]
                            stmt = self._apply_filter(stmt, column, operator, value)
                            logger.info(f"[QUERY ENGINE] Applied relational filter: {target_table_name}.{col_name} {operator} '{value}'")

        stmt = stmt.limit(min(limit, 200))
        result = await session.execute(stmt)
        rows = result.fetchall()

        output = []
        for row in rows:
            row_mapping = dict(row._mapping)
            full_record = {}

            # Populate direct entity attributes
            for attr_key, attr_def in entity_def.attributes.items():
                col_name = attr_def.column
                if col_name in row_mapping:
                    val = row_mapping[col_name]
                    full_record[attr_key] = str(val) if not isinstance(val, (int, float, bool, type(None))) else val

            # Dynamically enrich record with relationship properties
            await self._enrich_record_with_relationships(session, entity_def, full_record, row_mapping)

            # Apply select_fields projection if specified
            if select_fields:
                projected_record = {}
                for field in select_fields:
                    if field in full_record:
                        projected_record[field] = full_record[field]
                    else:
                        attr_def = entity_def.attributes.get(field)
                        col_name = attr_def.column if attr_def else field
                        if col_name in row_mapping:
                            val = row_mapping[col_name]
                            projected_record[field] = str(val) if not isinstance(val, (int, float, bool, type(None))) else val
                output.append(projected_record)
            else:
                output.append(full_record)

        logger.info(f"[QUERY ENGINE SUCCESS] Returning {len(output)} mapped records.")
        return output

    async def _enrich_record_with_relationships(
        self,
        session: AsyncSession,
        entity_def: EntityDefinition,
        record: dict[str, Any],
        raw_row_mapping: dict[str, Any],
    ) -> None:
        """Dynamically resolves and attaches relationship fields to an entity record dictionary."""
        raw_record_id = raw_row_mapping.get(entity_def.storage.id)
        if raw_record_id is None:
            return

        str_record_id = str(raw_record_id)

        for rel_name, rel_def in entity_def.relationships.items():
            target_entity_def = self._semantic_service.get_entity_details(rel_def.target)
            if not target_entity_def:
                continue

            target_table_name = target_entity_def.storage.table
            target_table = get_dynamic_table(target_table_name, self._semantic_service)
            target_entity_name = rel_def.target.lower()

            # 1. Many-To-One Relationship (e.g. Membre -> Paroisse via paroisse_id, Membre -> Zone via zone_geographique_id)
            if rel_def.cardinality in ("many-to-one", "one-to-one"):
                fk_candidates = [
                    f"{target_table_name}_id",
                    f"{rel_name}_id",
                    f"{target_entity_name}_id",
                ]
                fk_col = None
                for candidate in fk_candidates:
                    if candidate in raw_row_mapping and raw_row_mapping[candidate] is not None:
                        fk_col = candidate
                        break

                if fk_col and raw_row_mapping[fk_col] is not None:
                    fk_val = str(raw_row_mapping[fk_col])
                    stmt = select(target_table).where(target_table.c[target_entity_def.storage.id] == fk_val)
                    res = await session.execute(stmt)
                    rel_row = res.fetchone()
                    if rel_row:
                        m = rel_row._mapping
                        display_val = m.get("nom") or m.get("code") or m.get("name") or fk_val
                        record[rel_name] = display_val
                        record[f"{rel_name}.nom"] = display_val
                    else:
                        record[rel_name] = None
                        record[f"{rel_name}.nom"] = None
                else:
                    record[rel_name] = None
                    record[f"{rel_name}.nom"] = None

            # 2. Many-To-Many Relationship (e.g. Membre <-> Association via adhesion_association)
            elif rel_def.cardinality == "many-to-many" and rel_def.through:
                through_table_name = rel_def.through
                through_table = get_dynamic_table(through_table_name, self._semantic_service)

                primary_fk_candidates = [f"{entity_def.storage.table}_id"]
                target_fk_candidates = [f"{target_table_name}_id", f"{target_entity_name}_id"]

                primary_fk = next((c for c in primary_fk_candidates if c in through_table.c), None)
                target_fk = next((c for c in target_fk_candidates if c in through_table.c), None)

                if primary_fk and target_fk:
                    stmt = (
                        select(target_table)
                        .join(through_table, target_table.c[target_entity_def.storage.id] == through_table.c[target_fk])
                        .where(through_table.c[primary_fk] == str_record_id)
                    )
                    res = await session.execute(stmt)
                    rel_rows = res.fetchall()
                    names = []
                    for r in rel_rows:
                        m = r._mapping
                        val = m.get("nom") or m.get("code") or m.get("name")
                        if val:
                            names.append(str(val))
                    record[rel_name] = names
                    record[f"{rel_name}.nom"] = ", ".join(names) if names else None

            # 3. One-To-Many Relationship (e.g. Paroisse -> Membres or Association -> Membres)
            elif rel_def.cardinality == "one-to-many":
                primary_fk_candidates = [f"{entity_def.storage.table}_id"]
                primary_fk = next((c for c in primary_fk_candidates if c in target_table.c), None)

                if primary_fk:
                    stmt = select(target_table).where(target_table.c[primary_fk] == str_record_id)
                    res = await session.execute(stmt)
                    rel_rows = res.fetchall()
                    names = []
                    for r in rel_rows:
                        m = r._mapping
                        val = m.get("nom") or m.get("prenom") or m.get("code")
                        if val:
                            names.append(str(val))
                    record[rel_name] = names

    def _apply_filter(self, stmt, column, operator: str, value: Any):
        if operator == "equals":
            return stmt.where(column == value)
        elif operator == "contains":
            return stmt.where(column.ilike(f"%{value}%"))
        elif operator == "greater_than":
            return stmt.where(column > value)
        elif operator == "less_than":
            return stmt.where(column < value)
        return stmt
