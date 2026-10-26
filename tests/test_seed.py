import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from axora.data.dynamic_models import metadata
from axora.data.query_engine import QueryEngine
from axora.data.seed import seed_database
from axora.semantic.service import SemanticModelService

YAML_PATH = "src/axora/semantic/definitions/gestion_paroissiale.yaml"


@pytest_asyncio.fixture
async def seeded_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as session:
        seed_data = await seed_database(session)

    yield session_factory, seed_data
    await engine.dispose()


@pytest.fixture
def semantic_service():
    return SemanticModelService.from_yaml(YAML_PATH)


@pytest.mark.asyncio
async def test_seed_database_record_count(seeded_db, semantic_service):
    session_factory, seed_data = seeded_db
    query_engine = QueryEngine(semantic_service)

    assert len(seed_data["paroisses"]) == 2
    assert len(seed_data["zones"]) == 4
    assert len(seed_data["membres"]) == 4
    assert len(seed_data["associations"]) == 8

    async with session_factory() as session:
        membres = await query_engine.execute_query(session, "Membre")
        assert len(membres) == 4

        paroisses = await query_engine.execute_query(session, "Paroisse")
        assert len(paroisses) == 2

        assocs = await query_engine.execute_query(session, "Association")
        assert len(assocs) == 8


@pytest.mark.asyncio
async def test_seed_database_relational_query(seeded_db, semantic_service):
    session_factory, _ = seeded_db
    query_engine = QueryEngine(semantic_service)

    async with session_factory() as session:
        # Query members belonging to parish 'Andranovelona' and zone 'Andoharanofotsy'
        results = await query_engine.execute_query(
            session=session,
            entity_name="Membre",
            select_fields=["nom", "prenom", "statut_matrimonial"],
            filters=[
                {"path": "paroisse.nom", "operator": "equals", "value": "Andranovelona"},
                {"path": "zone.nom", "operator": "equals", "value": "Andoharanofotsy"},
            ],
        )
        assert len(results) == 2
        names = [r["nom"] for r in results]
        assert "Rakoto" in names
        assert "Rasoa" in names
