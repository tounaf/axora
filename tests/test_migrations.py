import pytest
import pytest_asyncio
from sqlalchemy import Column, MetaData, String, Table, inspect
from sqlalchemy.ext.asyncio import create_async_engine
from axora.data.migrations import DynamicSchemaMigrator
from axora.semantic.service import SemanticModelService

YAML_PATH = "src/axora/semantic/definitions/gestion_paroissiale.yaml"


@pytest_asyncio.fixture
async def migrator_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    semantic_service = SemanticModelService.from_yaml(YAML_PATH)
    migrator = DynamicSchemaMigrator(semantic_service, db_engine=engine)

    yield migrator, engine, semantic_service
    await engine.dispose()


@pytest.mark.asyncio
async def test_run_migrations_fresh_db(migrator_engine):
    migrator, engine, _ = migrator_engine

    # Run migration on clean in-memory DB
    actions = await migrator.run_migrations()

    assert len(actions["created_tables"]) >= 5
    assert "paroisse" in actions["created_tables"]
    assert "membre" in actions["created_tables"]

    # Verify via DB inspector
    async with engine.begin() as conn:
        def sync_inspect(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()

        tables = await conn.run_sync(sync_inspect)
        assert "paroisse" in tables
        assert "membre" in tables


@pytest.mark.asyncio
async def test_run_migrations_add_missing_column(migrator_engine):
    migrator, engine, _ = migrator_engine
    test_meta = MetaData()

    # 1. Pre-create a partial 'paroisse' table missing the 'nom' column
    partial_table = Table("paroisse", test_meta, Column("id", String, primary_key=True))
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: partial_table.create(sync_conn))

    # 2. Run migration engine to alter table and add missing 'nom' column
    actions = await migrator.run_migrations()

    assert "paroisse.nom" in actions["added_columns"] or "paroisse" in actions["created_tables"]
