import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from axora.agent.decisions import AgentDecision, ToolCall
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
async def e2e_environment():
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

    yield registry, semantic_service
    await engine.dispose()


@pytest.mark.asyncio
async def test_e2e_parish_membership_query(e2e_environment):
    registry, _ = e2e_environment

    # Simulate sequence of agent LLM decisions
    llm_decisions = [
        # Step 1: Discover model for concept 'Membre'
        AgentDecision(
            type="call_tool",
            tool_call=ToolCall(name="discover_model", arguments={"concept": "Membre"}),
        ),
        # Step 2: Execute query_data to retrieve members of Andranovelona in Andoharanofotsy zone
        AgentDecision(
            type="call_tool",
            tool_call=ToolCall(
                name="query_data",
                arguments={
                    "entity": "Membre",
                    "select": ["nom", "prenom", "statut_matrimonial"],
                    "filters": [
                        {"path": "paroisse.nom", "operator": "equals", "value": "Andranovelona"},
                        {"path": "zone.nom", "operator": "equals", "value": "Andoharanofotsy"},
                    ],
                },
            ),
        ),
        # Step 3: Final answer based on observed query results
        AgentDecision(
            type="final_answer",
            content="J'ai trouvé 2 membres dans la zone Andoharanofotsy de la paroisse Andranovelona : Jean Rakoto et Marie Rasoa.",
        ),
    ]

    llm_adapter = MockLLMAdapter(llm_decisions)
    runtime = AgentRuntime(tool_registry=registry, llm_adapter=llm_adapter)

    response = await runtime.process_intent(
        "Qui sont les membres de la paroisse Andranovelona qui habitent dans la zone d'Andoharanofotsy ?"
    )

    assert "2 membres" in response
    assert "Jean Rakoto" in response
    assert "Marie Rasoa" in response
