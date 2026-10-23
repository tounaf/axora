from pathlib import Path
import pytest
from axora.semantic.service import SemanticModelService
from axora.tools.discover_model import DiscoverModelTool
from axora.tools.registry import ToolRegistry

YAML_PATH = Path("src/axora/semantic/definitions/gestion_paroissiale.yaml")


@pytest.fixture
def semantic_service():
    return SemanticModelService.from_yaml(YAML_PATH)


@pytest.fixture
def discover_tool(semantic_service):
    return DiscoverModelTool(semantic_service)


@pytest.mark.asyncio
async def test_discover_tool_metadata(discover_tool):
    assert discover_tool.name == "discover_model"
    assert "Explore the semantic" in discover_tool.description
    assert discover_tool.parameters_schema["type"] == "object"


@pytest.mark.asyncio
async def test_discover_tool_overview(discover_tool):
    result = await discover_tool.execute({})
    assert result.status == "success"
    assert result.data["model_name"] == "gestion_paroissiale"
    assert len(result.data["entities"]) >= 5


@pytest.mark.asyncio
async def test_discover_tool_specific_concept(discover_tool):
    result = await discover_tool.execute({"concept": "Membre"})
    assert result.status == "success"
    assert result.data["concept"] == "Membre"
    assert "attributes" in result.data
    assert "relationships" in result.data
    assert "nom" in result.data["attributes"]


@pytest.mark.asyncio
async def test_discover_tool_synonym_resolution(discover_tool):
    result = await discover_tool.execute({"concept": "église"})
    assert result.status == "success"
    assert result.data["concept"] == "Paroisse"
    assert result.metadata["canonical_name"] == "Paroisse"


@pytest.mark.asyncio
async def test_discover_tool_unknown_concept(discover_tool):
    result = await discover_tool.execute({"concept": "ChoraleInexistante"})
    assert result.status == "error"
    assert result.error_code == "UNKNOWN_CONCEPT"
    assert "available_concepts" in result.data


def test_tool_registry_operations(discover_tool):
    registry = ToolRegistry()
    registry.register(discover_tool)

    assert registry.get("discover_model") is discover_tool
    assert len(registry.list_tools()) == 1

    schemas = registry.list_schemas()
    assert len(schemas) == 1
    assert schemas[0]["function"]["name"] == "discover_model"

    with pytest.raises(ValueError):
        registry.register(discover_tool)

    with pytest.raises(ValueError):
        registry.get("non_existent_tool")
