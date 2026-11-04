from typing import Any
from axora.semantic.service import SemanticModelService
from axora.views.interface import ColumnMetadata, ViewBuilderInterface, ViewPayload


class DynamicTableViewBuilder(ViewBuilderInterface):
    """Dynamically generates a rich table view payload with inferred column data types from the semantic model."""

    def __init__(self, semantic_service: SemanticModelService) -> None:
        self._semantic = semantic_service

    @property
    def view_type(self) -> str:
        return "table"

    def build(self, data: Any, entity_name: str | None = None, title: str | None = None, description: str | None = None, **kwargs: Any) -> ViewPayload:
        records: list[dict[str, Any]] = data if isinstance(data, list) else data.get("records", []) if isinstance(data, dict) else []
        entity = entity_name or (data.get("entity") if isinstance(data, dict) else "Données")

        entity_def = self._semantic.get_entity_details(entity) if entity else None

        columns: list[ColumnMetadata] = []
        if records:
            keys = list(records[0].keys())
            for key in keys:
                if key in ("id", f"{entity_def.storage.table}_id" if entity_def else None):
                    continue

                attr_def = entity_def.attributes.get(key) if entity_def else None

                # Determine data type dynamically
                if attr_def and attr_def.allowed_values:
                    data_type = "badge"
                    label = attr_def.description or key.capitalize().replace("_", " ")
                elif isinstance(records[0].get(key), list):
                    data_type = "tags"
                    label = key.capitalize().replace("_", " ")
                elif attr_def and attr_def.type == "date":
                    data_type = "date"
                    label = attr_def.description or key.capitalize().replace("_", " ")
                elif isinstance(records[0].get(key), (int, float)):
                    data_type = "number"
                    label = key.capitalize().replace("_", " ")
                else:
                    data_type = "string"
                    label = (attr_def.description if attr_def else key).capitalize().replace("_", " ")

                columns.append(ColumnMetadata(key=key, label=label, data_type=data_type, sortable=True))

        return ViewPayload(
            view_type="table",
            title=title or (f"Liste des {entity}s" if entity else "Tableau de Données"),
            description=description or f"{len(records)} enregistrement(s) trouvé(s)",
            data={
                "entity": entity,
                "columns": [col.model_dump() for col in columns],
                "rows": records,
                "total_count": len(records),
            },
        )


class DynamicChartViewBuilder(ViewBuilderInterface):
    """Generates charts (bar, pie/camembert, donut, line/courbe temporelle) dynamically from aggregated data."""

    @property
    def view_type(self) -> str:
        return "chart"

    def build(
        self,
        data: Any,
        chart_type: str = "bar",  # "bar", "pie", "donut", "line"
        title: str = "Statistiques",
        description: str | None = None,
        x_label: str = "Catégorie",
        y_label: str = "Valeur",
        **kwargs: Any
    ) -> ViewPayload:
        raw_series = data if isinstance(data, list) else data.get("series", []) if isinstance(data, dict) else []

        palette = [
            "#1d4ed8", "#0284c7", "#10b981", "#f59e0b",
            "#8b5cf6", "#ec4899", "#14b8a6", "#f97316",
        ]

        formatted_series = []
        for idx, item in enumerate(raw_series):
            if isinstance(item, dict):
                # Auto-detect label and value keys dynamically
                label = item.get("label") or item.get("name") or item.get("date") or item.get("key") or str(list(item.values())[0] if item else f"Item {idx + 1}")
                val = item.get("value") or item.get("count") or item.get("total")
                if val is None:
                    # Look for first numeric value in item dict
                    for v in item.values():
                        if isinstance(v, (int, float)):
                            val = v
                            break
                    if val is None:
                        val = 0

                color = item.get("color") or palette[idx % len(palette)]
                formatted_series.append({
                    "label": str(label),
                    "value": float(val) if isinstance(val, (int, float)) else 0,
                    "color": color,
                })

        return ViewPayload(
            view_type="chart",
            title=title,
            description=description,
            data={
                "chart_type": chart_type,
                "x_label": x_label,
                "y_label": y_label,
                "series": formatted_series,
                "total": sum(s["value"] for s in formatted_series),
            },
        )


class DynamicMetricCardsBuilder(ViewBuilderInterface):
    """Generates dynamic KPI indicator tiles with values, trends, and status indicators."""

    @property
    def view_type(self) -> str:
        return "metric_cards"

    def build(
        self,
        data: Any,
        title: str = "Indicateurs Clés (KPI)",
        description: str | None = None,
        **kwargs: Any
    ) -> ViewPayload:
        raw_cards = data if isinstance(data, list) else data.get("cards", []) if isinstance(data, dict) else []

        formatted_cards = []
        for idx, item in enumerate(raw_cards):
            if isinstance(item, dict):
                label = item.get("label") or item.get("title") or f"Indicateur {idx + 1}"
                val = item.get("value") or item.get("metric") or "0"
                desc = item.get("description") or item.get("subtitle")
                trend = item.get("trend")
                status = item.get("status") or item.get("trend_type") or "neutral"

                formatted_cards.append({
                    "label": str(label),
                    "value": str(val),
                    "description": str(desc) if desc else None,
                    "trend": str(trend) if trend else None,
                    "status": status if status in ("neutral", "success", "warning", "danger") else "neutral",
                })

        return ViewPayload(
            view_type="metric_cards",
            title=title,
            description=description,
            data={"cards": formatted_cards},
        )
