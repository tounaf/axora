from pathlib import Path
from typing import Any
from axora.extensions.bdd.introspector.db_introspector import LiveDatabaseIntrospector
from axora.extensions.bdd.introspector.interface import (
    ColumnInfo,
    DatabaseSchema,
    ForeignKeyInfo,
    SchemaIntrospectorInterface,
    TableInfo,
)
from axora.extensions.bdd.introspector.schema_reverse_engine import SchemaReverseEngine
from axora.extensions.bdd.introspector.sql_dump_parser import SQLDumpParser


def introspect_sql_file(
    sql_file: str | Path,
    output_yaml: str | Path | None = None,
    model_name: str | None = None,
) -> dict[str, Any]:
    """Parses a SQL DDL file, generates semantic model metadata, and optionally exports a YAML manifest."""
    parser = SQLDumpParser(sql_file, schema_name=model_name or Path(sql_file).stem)
    schema = parser.introspect()
    engine = SchemaReverseEngine(schema, model_name=model_name or schema.name)

    if output_yaml:
        engine.export_yaml(output_yaml)

    return engine.generate_manifest()


def introspect_live_db(
    connection_url: str,
    output_yaml: str | Path | None = None,
    model_name: str = "live_db",
) -> dict[str, Any]:
    """Connects to a live database, introspects tables, and generates a semantic model manifest."""
    introspector = LiveDatabaseIntrospector(connection_url, schema_name=model_name)
    schema = introspector.introspect()
    engine = SchemaReverseEngine(schema, model_name=model_name)

    if output_yaml:
        engine.export_yaml(output_yaml)

    return engine.generate_manifest()


__all__ = [
    "SchemaIntrospectorInterface",
    "DatabaseSchema",
    "TableInfo",
    "ColumnInfo",
    "ForeignKeyInfo",
    "SQLDumpParser",
    "LiveDatabaseIntrospector",
    "SchemaReverseEngine",
    "introspect_sql_file",
    "introspect_live_db",
]
