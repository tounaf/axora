import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from axora.agent.runtime import AgentRuntime
from axora.data.dynamic_models import build_dynamic_tables, metadata
from axora.data.seed import seed_database
from axora.llm.provider import MockLLMAdapter
from axora.semantic.service import SemanticModelService
from axora.tools.create_record import CreateRecordTool
from axora.tools.discover_model import DiscoverModelTool
from axora.tools.query_data import QueryDataTool
from axora.tools.registry import ToolRegistry

YAML_PATH = "src/axora/semantic/definitions/gestion_paroissiale.yaml"


@pytest_asyncio.fixture
async def seeded_environment():
    semantic_service = SemanticModelService.from_yaml(YAML_PATH)
    build_dynamic_tables(semantic_service)

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as session:
        await seed_database(session)

    registry = ToolRegistry()
    registry.register(DiscoverModelTool(semantic_service))
    registry.register(QueryDataTool(semantic_service, session_factory))
    registry.register(CreateRecordTool(semantic_service, session_factory))

    yield registry, semantic_service, session_factory
    await engine.dispose()


@pytest.mark.asyncio
async def test_dynamic_person_search_intent_rakoto_jean(seeded_environment):
    registry, _, _ = seeded_environment

    llm_adapter = MockLLMAdapter()
    runtime = AgentRuntime(tool_registry=registry, llm_adapter=llm_adapter)

    response = await runtime.process_intent("Qui est Rakoto Jean ?")

    assert "Rakoto" in response
    assert "Jean" in response


@pytest.mark.asyncio
async def test_dynamic_person_search_intent_rasoa_marie(seeded_environment):
    registry, _, _ = seeded_environment

    llm_adapter = MockLLMAdapter()
    runtime = AgentRuntime(tool_registry=registry, llm_adapter=llm_adapter)

    response = await runtime.process_intent("Détails de Rasoa Marie")

    assert "Rasoa" in response
    assert "Marie" in response


@pytest.mark.asyncio
async def test_dynamic_person_search_intent_not_found(seeded_environment):
    registry, _, _ = seeded_environment

    llm_adapter = MockLLMAdapter()
    runtime = AgentRuntime(tool_registry=registry, llm_adapter=llm_adapter)

    response = await runtime.process_intent("Qui est Dupont Pierre ?")

    assert "Aucun" in response or "non" in response
