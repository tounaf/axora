from typing import Any
from sqlalchemy import Column, Date, MetaData, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR
import uuid
from axora.semantic.service import SemanticModelService


class GUID(TypeDecorator):
    """Platform-independent GUID type. Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing stringified UUID."""
    impl = CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(uuid.UUID(str(value)))


# Shared SQLAlchemy MetaData
metadata = MetaData()

# Registry storing dynamically generated SQLAlchemy Table objects
DYNAMIC_TABLES: dict[str, Table] = {}


def build_dynamic_tables(semantic_service: SemanticModelService) -> dict[str, Table]:
    """Dynamically builds SQLAlchemy Table instances directly from the Semantic Model Manifest."""
    global DYNAMIC_TABLES

    # Clear metadata and registry before building to prevent table collision issues across test runs
    DYNAMIC_TABLES.clear()
    metadata.clear()

    # Pass 1: Declare all tables with primary key, attributes, and relationship foreign keys
    for entity_name in semantic_service.get_entity_names():
        entity_def = semantic_service.get_entity_details(entity_name)
        if not entity_def:
            continue

        table_name = entity_def.storage.table
        if table_name in DYNAMIC_TABLES:
            continue

        added_cols = set()
        columns = []

        # Primary Key Column (GUID)
        pk_name = entity_def.storage.id
        columns.append(Column(pk_name, GUID, primary_key=True))
        added_cols.add(pk_name)

        # Dynamic Attributes
        for attr_name, attr_def in entity_def.attributes.items():
            col_name = attr_def.column
            if col_name in added_cols:
                continue

            if attr_def.type == "date":
                columns.append(Column(col_name, Date, nullable=True))
            elif attr_def.type == "string" and col_name.endswith("_id"):
                columns.append(Column(col_name, GUID, nullable=True))
            elif attr_def.type == "string":
                columns.append(Column(col_name, String(200), nullable=True))
            else:
                columns.append(Column(col_name, Text, nullable=True))

            added_cols.add(col_name)

        # Dynamic Relational Foreign Key Columns (e.g., paroisse_id, zone_geographique_id)
        for rel_name, rel_def in entity_def.relationships.items():
            if rel_def.cardinality in ("many-to-one", "one-to-one"):
                target_entity_def = semantic_service.get_entity_details(rel_def.target)
                if target_entity_def:
                    fk_col_1 = f"{target_entity_def.storage.table}_id"
                    fk_col_2 = f"{rel_name}_id"
                    for fk in (fk_col_1, fk_col_2):
                        if fk not in added_cols:
                            columns.append(Column(fk, GUID, nullable=True))
                            added_cols.add(fk)

        table_obj = Table(table_name, metadata, *columns, extend_existing=True)
        DYNAMIC_TABLES[table_name] = table_obj

    return DYNAMIC_TABLES


def get_dynamic_table(table_name: str, semantic_service: SemanticModelService) -> Table:
    """Retrieves or dynamically builds a SQLAlchemy Table by table name."""
    if table_name not in DYNAMIC_TABLES:
        build_dynamic_tables(semantic_service)
    if table_name not in DYNAMIC_TABLES:
        raise ValueError(f"Dynamic table for '{table_name}' could not be generated from semantic model.")
    return DYNAMIC_TABLES[table_name]
