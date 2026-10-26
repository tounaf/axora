from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from axora.data.models import Association, AdhesionAssociation, Membre, Paroisse, ZoneGeographique
from axora.semantic.service import SemanticModelService

# Map SQL table names (dynamically derived from semantic model storage.table) to SQLAlchemy ORM models
TABLE_TO_MODEL_MAP = {
    model_cls.__tablename__: model_cls
    for model_cls in (Paroisse, ZoneGeographique, Membre, Association, AdhesionAssociation)
}


class QueryEngine:
    """Translates structured semantic queries into safe, parameterized SQLAlchemy async queries dynamically using the semantic model manifest."""

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
        model_cls = TABLE_TO_MODEL_MAP.get(table_name)
        if not model_cls:
            raise ValueError(f"No ORM mapping found for table '{table_name}' associated with entity '{entity_name}'")

        stmt = select(model_cls)
        joined_models = set()
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
                column_name = attr_def.column if attr_def else attr_name
                column = getattr(model_cls, column_name, None)
                if column is not None:
                    stmt = self._apply_filter(stmt, column, operator, value)

            elif len(parts) == 2:
                rel_name, target_attr = parts[0], parts[1]
                rel_def = entity_def.relationships.get(rel_name)

                if rel_def:
                    target_entity_def = self._semantic_service.get_entity_details(rel_def.target)
                    if target_entity_def:
                        target_table = target_entity_def.storage.table
                        target_model_cls = TABLE_TO_MODEL_MAP.get(target_table)

                        if target_model_cls and target_model_cls not in joined_models and target_model_cls != model_cls:
                            # Dynamic join based on ORM relationship attribute or relationship target
                            rel_attr = getattr(model_cls, rel_name, None)
                            if rel_attr is not None:
                                stmt = stmt.join(rel_attr)
                            else:
                                stmt = stmt.join(target_model_cls)
                            joined_models.add(target_model_cls)

                        target_attr_def = target_entity_def.attributes.get(target_attr)
                        col_name = target_attr_def.column if target_attr_def else target_attr
                        column = getattr(target_model_cls, col_name, None) if target_model_cls else None
                        if column is not None:
                            stmt = self._apply_filter(stmt, column, operator, value)

        stmt = stmt.limit(min(limit, 200))
        result = await session.execute(stmt)
        records = result.scalars().all()

        output = []
        for record in records:
            row_dict = {}
            if select_fields:
                for field in select_fields:
                    attr_def = entity_def.attributes.get(field)
                    col_name = attr_def.column if attr_def else field
                    if hasattr(record, col_name):
                        val = getattr(record, col_name)
                        row_dict[field] = str(val) if not isinstance(val, (int, float, bool, type(None))) else val
            else:
                for attr_key, attr_def in entity_def.attributes.items():
                    col_name = attr_def.column
                    if hasattr(record, col_name):
                        val = getattr(record, col_name)
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
