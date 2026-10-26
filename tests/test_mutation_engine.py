import datetime
import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from axora.data.models import Base, Paroisse, ZoneGeographique
from axora.data.mutation_engine import BusinessRuleViolation, MutationEngine
from axora.semantic.service import SemanticModelService
from axora.tools.create_record import CreateRecordTool
from axora.tools.update_record import UpdateRecordTool

YAML_PATH = "src/axora/semantic/definitions/gestion_paroissiale.yaml"


@pytest_asyncio.fixture
async def in_memory_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as session:
        p1 = Paroisse(nom="Andranovelona")
        p2 = Paroisse(nom="Analamanga")
        session.add_all([p1, p2])
        await session.flush()

        z1 = ZoneGeographique(paroisse_id=p1.id, nom="Andoharanofotsy")
        z2 = ZoneGeographique(paroisse_id=p2.id, nom="ZoneAutre")
        session.add_all([z1, z2])
        await session.commit()

        p1_id, p2_id, z1_id, z2_id = p1.id, p2.id, z1.id, z2.id

    yield session_factory, p1_id, p2_id, z1_id, z2_id
    await engine.dispose()


@pytest.fixture
def semantic_service():
    return SemanticModelService.from_yaml(YAML_PATH)


@pytest.mark.asyncio
async def test_create_membre_success(in_memory_db, semantic_service):
    session_factory, p1_id, _, z1_id, _ = in_memory_db
    engine = MutationEngine(semantic_service)

    async with session_factory() as session:
        record = await engine.create_record(
            session=session,
            entity_name="Membre",
            payload={
                "paroisse_id": p1_id,
                "zone_geographique_id": z1_id,
                "nom": "Rakoto",
                "prenom": "Paul",
                "sexe": "HOMME",
                "date_naissance": datetime.date(1990, 1, 1),
                "statut_matrimonial": "MARIE",
            },
        )
        assert "id" in record
        assert record["nom"] == "Rakoto"


@pytest.mark.asyncio
async def test_create_membre_zone_mismatch_rule_violation(in_memory_db, semantic_service):
    session_factory, p1_id, _, _, z2_id = in_memory_db
    engine = MutationEngine(semantic_service)

    # z2 belongs to p2, trying to associate it with p1
    async with session_factory() as session:
        with pytest.raises(BusinessRuleViolation) as exc_info:
            await engine.create_record(
                session=session,
                entity_name="Membre",
                payload={
                    "paroisse_id": p1_id,
                    "zone_geographique_id": z2_id,
                    "nom": "Rasoa",
                    "prenom": "Liva",
                    "sexe": "FEMME",
                    "date_naissance": datetime.date(1995, 2, 2),
                    "statut_matrimonial": "CELIBATAIRE",
                },
            )
        assert "BR-001" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_record_tool_success(in_memory_db, semantic_service):
    session_factory, _, _, _, _ = in_memory_db
    tool = CreateRecordTool(semantic_service, session_factory)

    result = await tool.execute({
        "entity": "Paroisse",
        "payload": {"nom": "Nouvelle Paroisse Unique"}
    })
    assert result.status == "success"
    assert result.data["record"]["nom"] == "Nouvelle Paroisse Unique"


@pytest.mark.asyncio
async def test_update_record_tool_success(in_memory_db, semantic_service):
    session_factory, p1_id, _, z1_id, _ = in_memory_db
    create_tool = CreateRecordTool(semantic_service, session_factory)
    update_tool = UpdateRecordTool(semantic_service, session_factory)

    res_create = await create_tool.execute({
        "entity": "Membre",
        "payload": {
            "paroisse_id": str(p1_id),
            "zone_geographique_id": str(z1_id),
            "nom": "AncienNom",
            "prenom": "Jean",
            "sexe": "HOMME",
            "date_naissance": "1992-04-04",
            "statut_matrimonial": "CELIBATAIRE",
        }
    })
    membre_id = res_create.data["record"]["id"]

    res_update = await update_tool.execute({
        "entity": "Membre",
        "record_id": membre_id,
        "payload": {"nom": "NouveauNom"}
    })
    assert res_update.status == "success"
    assert res_update.data["record"]["nom"] == "NouveauNom"
