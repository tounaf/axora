from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from axora.data.models import Association, AdhesionAssociation, Membre, Paroisse, ZoneGeographique
from axora.semantic.service import SemanticModelService

MODEL_MAP = {
    "Paroisse": Paroisse,
    "ZoneGeographique": ZoneGeographique,
    "Membre": Membre,
    "Association": Association,
    "AdhesionAssociation": AdhesionAssociation,
}


class QueryEngine:
    """Translates structured semantic queries into safe, parameterized SQLAlchemy async queries."""

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
        canonical_entity = self._semantic_service.resolve_concept_name(entity_name)
        if not canonical_entity or canonical_entity not in MODEL_MAP:
            raise ValueError(f"Unknown target entity: '{entity_name}'")

        model_cls = MODEL_MAP[canonical_entity]
        stmt = select(model_cls)

        # Apply joins and filters based on semantic paths
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
                field_name = parts[0]
                column = getattr(model_cls, field_name, None)
                if column is not None:
                    stmt = self._apply_filter(stmt, column, operator, value)
            elif len(parts) == 2:
                rel_name, field_name = parts[0], parts[1]
                if rel_name == "paroisse" and model_cls != Paroisse:
                    if Paroisse not in joined_models:
                        stmt = stmt.join(model_cls.paroisse)
                        joined_models.add(Paroisse)
                    column = getattr(Paroisse, field_name, None)
                    if column is not None:
                        stmt = self._apply_filter(stmt, column, operator, value)
                elif rel_name in ("zone", "zones") and model_cls != ZoneGeographique:
                    if ZoneGeographique not in joined_models:
                        stmt = stmt.join(model_cls.zone if hasattr(model_cls, "zone") else model_cls.zones)
                        joined_models.add(ZoneGeographique)
                    column = getattr(ZoneGeographique, field_name, None)
                    if column is not None:
                        stmt = self._apply_filter(stmt, column, operator, value)

        stmt = stmt.limit(min(limit, 200))
        result = await session.execute(stmt)
        records = result.scalars().all()

        output = []
        for record in records:
            row_dict = {}
            fields_to_extract = select_fields if select_fields else [
                c.name for c in record.__table__.columns
            ]
            for field in fields_to_extract:
                if hasattr(record, field):
                    val = getattr(record, field)
                    row_dict[field] = str(val) if not isinstance(val, (int, float, bool, type(None))) else val
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
