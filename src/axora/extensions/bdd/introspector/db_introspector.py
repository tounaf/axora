import logging
from typing import Any
from axora.extensions.bdd.introspector.interface import (
    ColumnInfo,
    DatabaseSchema,
    ForeignKeyInfo,
    SchemaIntrospectorInterface,
    TableInfo,
)

logger = logging.getLogger("axora.extensions.bdd.introspector.db")


class LiveDatabaseIntrospector(SchemaIntrospectorInterface):
    """Introspects a live database connection using SQLAlchemy Inspector."""

    def __init__(self, connection_url: str, schema_name: str = "live_db") -> None:
        self.connection_url = connection_url
        self.schema_name = schema_name

    def introspect(self) -> DatabaseSchema:
        from sqlalchemy import create_engine, inspect

        sync_url = self._to_sync_url(self.connection_url)
        engine = create_engine(sync_url)
        inspector = inspect(engine)

        tables: dict[str, TableInfo] = {}
        table_names = inspector.get_table_names()

        for tbl_name in table_names:
            table_info = TableInfo(name=tbl_name)

            # 1. Primary keys
            pk_constraint = inspector.get_pk_constraint(tbl_name) or {}
            table_info.primary_key = pk_constraint.get("constrained_columns", [])

            # 2. Columns
            for col in inspector.get_columns(tbl_name):
                c_name = col["name"]
                sql_type = str(col["type"]).lower()
                is_nullable = col.get("nullable", True)
                is_pk = c_name in table_info.primary_key
                comment = col.get("comment")

                semantic_type = self._map_type_to_semantic(sql_type, c_name)

                table_info.columns[c_name] = ColumnInfo(
                    name=c_name,
                    sql_type=sql_type,
                    semantic_type=semantic_type,
                    is_nullable=is_nullable,
                    is_primary_key=is_pk,
                    comment=comment,
                )

            # 3. Foreign keys
            for fk in inspector.get_foreign_keys(tbl_name):
                constrained_cols = fk.get("constrained_columns", [])
                referred_table = fk.get("referred_table")
                referred_cols = fk.get("referred_columns", [])
                c_name = fk.get("name")

                if constrained_cols and referred_table and referred_cols:
                    table_info.foreign_keys.append(
                        ForeignKeyInfo(
                            constrained_column=constrained_cols[0],
                            referred_table=referred_table,
                            referred_column=referred_cols[0],
                            constraint_name=c_name,
                        )
                    )

            # 4. Junction table detection
            if len(table_info.foreign_keys) == 2:
                fk_cols = {fk.constrained_column for fk in table_info.foreign_keys}
                if set(table_info.primary_key) == fk_cols or len(table_info.columns) <= 4:
                    table_info.is_junction = True

            tables[tbl_name] = table_info

        engine.dispose()
        return DatabaseSchema(name=self.schema_name, tables=tables)

    def _to_sync_url(self, url: str) -> str:
        """Converts async SQLAlchemy URLs (e.g., +asyncpg, +aiomysql, +aiosqlite) to sync drivers for inspect."""
        sync_url = url
        for async_driver in ("+asyncpg", "+psycopg", "+aiomysql", "+asyncmy", "+aiosqlite"):
            sync_url = sync_url.replace(async_driver, "")

        if sync_url.startswith("postgresql://"):
            return sync_url.replace("postgresql://", "postgresql+psycopg://", 1)
        if sync_url.startswith("mysql://"):
            return sync_url.replace("mysql://", "mysql+pymysql://", 1)
        if sync_url.startswith("mariadb://"):
            return sync_url.replace("mariadb://", "mysql+pymysql://", 1)
        return sync_url

    def _map_type_to_semantic(self, sql_type: str, col_name: str) -> str:
        t = sql_type.lower()
        if "bool" in t:
            return "boolean"
        if any(num in t for num in ("int", "decimal", "numeric", "float", "double")):
            return "number"
        if any(dt in t for dt in ("date", "time", "timestamp")):
            return "date"
        if "text" in t:
            return "text"
        return "string"
