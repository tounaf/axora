from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from axora.main import app
from axora.semantic.service import SemanticModelService
from axora.tools.render_view import RenderViewTool
from axora.views.builders import (
    DynamicChartViewBuilder,
    DynamicMetricCardsBuilder,
    DynamicTableViewBuilder,
)
from axora.views.registry import ViewRegistry

YAML_PATH = Path("src/axora/semantic/definitions/gestion_paroissiale.yaml")
client = TestClient(app)


def test_view_registry_registration():
    registry = ViewRegistry()
    semantic_service = SemanticModelService.from_yaml(YAML_PATH)
    table_builder = DynamicTableViewBuilder(semantic_service)

    registry.register(table_builder)
    assert registry.has("table")
    assert registry.get("table") is table_builder
    assert "table" in registry.list_types()

    with pytest.raises(ValueError, match="already registered"):
        registry.register(table_builder)

    with pytest.raises(ValueError, match="Unknown view type"):
        registry.get("unknown_type")


def test_dynamic_table_view_builder_type_inference():
    semantic_service = SemanticModelService.from_yaml(YAML_PATH)
    builder = DynamicTableViewBuilder(semantic_service)

    sample_records = [
        {
            "nom": "Rakoto",
            "prenom": "Jean",
            "statut_matrimonial": "CELIBATAIRE",
            "date_naissance": "1992-04-15",
            "associations": ["Association des Jeunes"],
            "age": 32,
        }
    ]

    view_payload = builder.build(sample_records, entity_name="Membre")
    assert view_payload.view_type == "table"
    assert view_payload.data["total_count"] == 1

    cols = {c["key"]: c for c in view_payload.data["columns"]}
    assert cols["nom"]["data_type"] == "string"
    assert cols["statut_matrimonial"]["data_type"] == "badge"
    assert cols["date_naissance"]["data_type"] == "date"
    assert cols["associations"]["data_type"] == "tags"
    assert cols["age"]["data_type"] == "number"


def test_dynamic_chart_view_builder():
    builder = DynamicChartViewBuilder()
    data = [
        {"label": "Andranovelona", "value": 2},
        {"label": "Analamanga", "value": 2},
    ]

    payload = builder.build(data, chart_type="bar", title="Répartition par Paroisse")
    assert payload.view_type == "chart"
    assert payload.data["chart_type"] == "bar"
    assert len(payload.data["series"]) == 2
    assert payload.data["series"][0]["label"] == "Andranovelona"
    assert payload.data["series"][0]["value"] == 2
    assert "color" in payload.data["series"][0]


def test_dynamic_metric_cards_builder():
    builder = DynamicMetricCardsBuilder()
    cards = [
        {"label": "Total Membres", "value": "4", "status": "neutral"},
        {"label": "Paroisses Actives", "value": "2", "status": "success"},
    ]

    payload = builder.build(cards, title="Indicateurs Globaux")
    assert payload.view_type == "metric_cards"
    assert len(payload.data["cards"]) == 2


@pytest.mark.asyncio
async def test_render_view_tool_execution():
    semantic_service = SemanticModelService.from_yaml(YAML_PATH)
    registry = ViewRegistry()
    registry.register(DynamicTableViewBuilder(semantic_service))
    registry.register(DynamicChartViewBuilder())

    tool = RenderViewTool(registry)
    assert tool.name == "render_view"

    # Test table render
    res = await tool.execute({
        "view_type": "table",
        "title": "Membres",
        "data": [{"nom": "Rasoa", "prenom": "Marie"}],
    })
    assert res.status == "success"
    assert res.data["view_type"] == "table"

    # Test unsupported view type
    err_res = await tool.execute({
        "view_type": "unregistered_type",
        "data": {},
    })
    assert err_res.status == "error"
    assert err_res.error_code == "UNSUPPORTED_VIEW_TYPE"


def test_api_view_types_endpoint():
    response = client.get("/api/v1/views/types")
    assert response.status_code == 200
    types = response.json()["view_types"]
    assert "table" in types
    assert "chart" in types
    assert "metric_cards" in types
