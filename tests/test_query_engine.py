import datetime
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from axora.data.dynamic_models import build_dynamic_tables, metadata
from axora.data.mutation_engine import MutationEngine
from axora.data.query_engine import QueryEngine
from axora.semantic.service import SemanticModelService
from axora.tools.query_data import QueryDataTool

YAML_PATH = "src/axora/semantic/definitions/gestion_paroissiale.yaml"


@pytest_asyncio.fixture
async def in_memory_db():
    semantic_service = SemanticModelService.from_yaml(YAML_PATH)
    build_dynamic_tables(semantic_service)

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    mutation_engine = MutationEngine(semantic_service)

    async with session_factory() as session:
        async with session.begin():
            p1 = await mutation_engine.create_record(session, "Paroisse", {"nom": "Andranovelona"})
            z1 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p1["id"], "nom": "Andoharanofotsy"})

            await mutation_engine.create_record(session, "Membre", {
                "paroisse_id": p1["id"],
                "zone_geographique_id": z1["id"],
                "nom": "Rabe",
                "prenom": "Jean",
                "sexe": "HOMME",
                "date_naissance": "1995-05-10",
                "statut_matrimonial": "CELIBATAIRE",
            })
            await mutation_engine.create_record(session, "Membre", {
                "paroisse_id": p1["id"],
                "zone_geographique_id": z1["id"],
                "nom": "Rasoa",
                "prenom": "Marie",
                "sexe": "FEMME",
                "date_naissance": "1998-08-15",
                "statut_matrimonial": "CELIBATAIRE",
            })

    yield session_factory
    await engine.dispose()


@pytest.fixture
def semantic_service():
    return SemanticModelService.from_yaml(YAML_PATH)


@pytest.mark.asyncio
async def test_query_engine_direct_filter(in_memory_db, semantic_service):
    engine = QueryEngine(semantic_service)
    async with in_memory_db() as session:
        results = await engine.execute_query(
            session=session,
            entity_name="Membre",
            select_fields=["nom", "prenom", "statut_matrimonial"],
            filters=[{"path": "nom", "operator": "equals", "value": "Rabe"}],
        )
        assert len(results) == 1
        assert results[0]["nom"] == "Rabe"
        assert results[0]["prenom"] == "Jean"


@pytest.mark.asyncio
async def test_query_engine_relational_filter(in_memory_db, semantic_service):
    engine = QueryEngine(semantic_service)
    async with in_memory_db() as session:
        results = await engine.execute_query(
            session=session,
            entity_name="Membre",
            select_fields=["nom", "prenom"],
            filters=[
                {"path": "paroisse.nom", "operator": "equals", "value": "Andranovelona"},
                {"path": "zone.nom", "operator": "equals", "value": "Andoharanofotsy"},
            ],
        )
        assert len(results) == 2


@pytest.mark.asyncio
async def test_query_data_tool_execution(in_memory_db, semantic_service):
    tool = QueryDataTool(semantic_service, in_memory_db)
    result = await tool.execute(
        {
            "entity": "Membre",
            "select": ["nom", "prenom"],
            "filters": [{"path": "paroisse.nom", "operator": "equals", "value": "Andranovelona"}],
        }
    )
    assert result.status == "success"
    assert result.data["entity"] == "Membre"
    assert result.data["count"] == 2
