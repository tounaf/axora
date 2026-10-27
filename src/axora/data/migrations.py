import asyncio
import logging
from pathlib import Path
from sqlalchemy import Column, Date, Inspector, MetaData, String, Table, Text, inspect, select, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from axora.data.database import engine
from axora.data.dynamic_models import build_dynamic_tables
from axora.semantic.service import SemanticModelService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("axora.migrations")

YAML_PATH = Path("src/axora/semantic/definitions/gestion_paroissiale.yaml")


class DynamicSchemaMigrator:
    """Engine responsible for comparing the Semantic Model Manifest with the target DB schema and applying automatic DDL migrations."""

    def __init__(self, semantic_service: SemanticModelService, db_engine: AsyncEngine = engine) -> None:
        self._semantic_service = semantic_service
        self._engine = db_engine

    async def run_migrations(self) -> dict[str, list[str]]:
        """Compares target database tables and columns against the semantic model manifest and applies schema updates automatically."""
        logger.info("Starting automatic database schema migration...")
        target_tables = build_dynamic_tables(self._semantic_service)

        applied_actions = {"created_tables": [], "added_columns": []}

        async with self._engine.begin() as conn:
            # Sync inspection of existing tables and columns
            def sync_inspect(connection):
                inspector = inspect(connection)
                return {
                    t_name: [col["name"] for col in inspector.get_columns(t_name)]
                    for t_name in inspector.get_table_names()
                }

            existing_db_schema = await conn.run_sync(sync_inspect)

            for table_name, table_obj in target_tables.items():
                if table_name not in existing_db_schema:
                    logger.info(f"[*] Creating new missing table: '{table_name}'")
                    await conn.run_sync(lambda sync_conn, t=table_obj: t.create(sync_conn))
                    applied_actions["created_tables"].append(table_name)
                else:
                    existing_cols = existing_db_schema[table_name]
                    for column in table_obj.columns:
                        if column.name not in existing_cols:
                            logger.info(f"[*] Adding missing column '{column.name}' to table '{table_name}'...")
                            col_type_sql = str(column.type.compile(self._engine.dialect))
                            alter_stmt = text(f'ALTER TABLE "{table_name}" ADD COLUMN "{column.name}" {col_type_sql}')
                            await conn.execute(alter_stmt)
                            applied_actions["added_columns"].append(f"{table_name}.{column.name}")

        logger.info(f"Schema Migration Completed. Created Tables: {len(applied_actions['created_tables'])}, Added Columns: {len(applied_actions['added_columns'])}")
        return applied_actions


async def migrate_cli_main():
    yaml_path = Path("src/axora/semantic/definitions/gestion_paroissiale.yaml")
    semantic_service = SemanticModelService.from_yaml(yaml_path)
    migrator = DynamicSchemaMigrator(semantic_service)
    await migrator.run_migrations()


if __name__ == "__main__":
    asyncio.run(migrate_cli_main())
