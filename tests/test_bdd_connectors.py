import pytest
import pytest_asyncio
from axora.data.mutation_engine import BusinessRuleViolation
from axora.extensions.bdd import (
    ConnectorRegistry,
    DatabaseConnectorInterface,
    PostgresConnector,
    SqliteConnector,
    connector_registry,
    get_connector,
)
from axora.semantic.service import SemanticModelService

YAML_PATH = "src/axora/semantic/definitions/gestion_paroissiale.yaml"


@pytest.fixture
def semantic_service():
    return SemanticModelService.from_yaml(YAML_PATH)


def test_connector_registry_defaults():
    schemes = connector_registry.list_schemes()
    assert "postgresql" in schemes
    assert "postgresql+psycopg" in schemes
    assert "sqlite" in schemes
    assert "sqlite+aiosqlite" in schemes


def test_connector_registry_custom_registration():
    custom_registry = ConnectorRegistry()

    class FakeConnector(DatabaseConnectorInterface):
        @property
        def dialect_name(self) -> str:
            return "fake"

        @property
        def is_nosql(self) -> bool:
            return False

        async def connect(self) -> None:
            pass

        async def disconnect(self) -> None:
            pass

        async def health_check(self):
            return {"status": "ok"}

        async def execute_query(self, entity_def, select_fields=None, filters=None, limit=50):
            return []

        async def execute_mutation(self, entity_def, action, payload, record_id=None):
            return {}

    custom_registry.register("fake", FakeConnector)
    assert custom_registry.has_scheme("fake")
    assert custom_registry.get("fake") is FakeConnector

    with pytest.raises(ValueError, match="No database connector registered"):
        custom_registry.get("unknown_db")

    with pytest.raises(ValueError, match="Missing scheme delimiter"):
        custom_registry._extract_scheme("invalid-url-without-scheme")


def test_url_normalization():
    pg = PostgresConnector("postgresql://user:pass@localhost:5432/axora")
    assert pg.dialect_name == "postgresql"
    assert pg._normalize_url(pg.raw_url).startswith("postgresql+psycopg://")
    assert pg.is_nosql is False

    sqlite = SqliteConnector("sqlite:///path/to/test.db")
    assert sqlite.dialect_name == "sqlite"
    assert sqlite._normalize_url(sqlite.raw_url).startswith("sqlite+aiosqlite://")
    assert sqlite.is_nosql is False


@pytest.mark.asyncio
async def test_sqlite_connector_lifecycle():
    connector = SqliteConnector("sqlite+aiosqlite:///:memory:")
    await connector.connect()
    assert connector.engine is not None

    health = await connector.health_check()
    assert health["status"] == "ok"
    assert health["dialect"] == "sqlite"
    assert "latency_ms" in health

    await connector.disconnect()


@pytest.mark.asyncio
async def test_sqlite_connector_semantic_operations(semantic_service):
    connector = SqliteConnector("sqlite+aiosqlite:///:memory:", semantic_service=semantic_service)
    await connector.connect()
    await connector.init_schema()

    paroisse_def = semantic_service.get_entity_details("Paroisse")
    assert paroisse_def is not None

    # 1. Create Paroisse
    created_p = await connector.execute_mutation(
        entity_def=paroisse_def,
        action="create",
        payload={"nom": "Andranovelona"},
    )
    assert "id" in created_p
    assert created_p["nom"] == "Andranovelona"

    # 2. Query Paroisse
    records = await connector.execute_query(
        entity_def=paroisse_def,
        filters=[{"path": "nom", "operator": "equals", "value": "Andranovelona"}],
    )
    assert len(records) == 1
    assert records[0]["nom"] == "Andranovelona"

    # 3. Create Zone
    zone_def = semantic_service.get_entity_details("ZoneGeographique")
    created_z = await connector.execute_mutation(
        entity_def=zone_def,
        action="create",
        payload={"nom": "Andoharanofotsy", "paroisse_id": created_p["id"]},
    )
    assert "id" in created_z

    # 4. Update Zone
    updated_z = await connector.execute_mutation(
        entity_def=zone_def,
        action="update",
        record_id=created_z["id"],
        payload={"nom": "Andoharanofotsy-Nord"},
    )
    assert updated_z["nom"] == "Andoharanofotsy-Nord"

    await connector.disconnect()


@pytest.mark.asyncio
async def test_sqlite_connector_validation_error(semantic_service):
    connector = SqliteConnector("sqlite+aiosqlite:///:memory:", semantic_service=semantic_service)
    await connector.connect()
    await connector.init_schema()

    membre_def = semantic_service.get_entity_details("Membre")

    # Attempting to insert invalid matrimonial status must raise BusinessRuleViolation
    with pytest.raises(BusinessRuleViolation, match="Valeur 'DIVORCE' non autorisée"):
        await connector.execute_mutation(
            entity_def=membre_def,
            action="create",
            payload={
                "nom": "Rakoto",
                "prenom": "Paul",
                "sexe": "HOMME",
                "statut_matrimonial": "DIVORCE",
            },
        )

    await connector.disconnect()


def test_get_connector_factory(semantic_service):
    sqlite_conn = get_connector("sqlite+aiosqlite:///:memory:", semantic_service=semantic_service)
    assert isinstance(sqlite_conn, SqliteConnector)

    pg_conn = get_connector("postgresql://localhost:5432/axora", semantic_service=semantic_service)
    assert isinstance(pg_conn, PostgresConnector)
