from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from axora.data.dynamic_models import get_dynamic_table
from axora.semantic.service import SemanticModelService


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
            raise ValueError(f"Unknown target entity or synonym: '{entity_name}'")

        table_name = entity_def.storage.table
        primary_table = get_dynamic_table(table_name, self._semantic_service)

        stmt = select(primary_table)
        joined_tables = set()
        filters = filters or []

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

            elif len(parts) == 2:
                rel_name, target_attr = parts[0], parts[1]
                rel_def = entity_def.relationships.get(rel_name)

                if rel_def:
                    target_entity_def = self._semantic_service.get_entity_details(rel_def.target)
                    if target_entity_def:
                        target_table_name = target_entity_def.storage.table
                        target_table = get_dynamic_table(target_table_name, self._semantic_service)

                        if target_table_name not in joined_tables and target_table_name != table_name:
                            # Join dynamically on matching foreign key column name
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

                        target_attr_def = target_entity_def.attributes.get(target_attr)
                        col_name = target_attr_def.column if target_attr_def else target_attr
                        if col_name in target_table.c:
                            column = target_table.c[col_name]
                            stmt = self._apply_filter(stmt, column, operator, value)

        stmt = stmt.limit(min(limit, 200))
        result = await session.execute(stmt)
        rows = result.fetchall()

        output = []
        for row in rows:
            row_dict = {}
            row_mapping = row._mapping
            if select_fields:
                for field in select_fields:
                    attr_def = entity_def.attributes.get(field)
                    col_name = attr_def.column if attr_def else field
                    if col_name in row_mapping:
                        val = row_mapping[col_name]
                        row_dict[field] = str(val) if not isinstance(val, (int, float, bool, type(None))) else val
            else:
                for attr_key, attr_def in entity_def.attributes.items():
                    col_name = attr_def.column
                    if col_name in row_mapping:
                        val = row_mapping[col_name]
                        row_dict[attr_key] = str(val) if not isinstance(val, (int, float, bool, type(None))) else val

            output.append(row_dict)

        return output

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
