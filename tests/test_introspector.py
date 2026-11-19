import os
import subprocess
import sys
from pathlib import Path
import pytest
from axora.extensions.bdd.introspector import (
    LiveDatabaseIntrospector,
    SQLDumpParser,
    SchemaReverseEngine,
    introspect_sql_file,
)

SQL_FILE = "fvavitao_identity.sql"


def test_sql_dump_parser_fvavitao():
    """Verify that SQLDumpParser parses fvavitao_identity.sql correctly."""
    parser = SQLDumpParser(SQL_FILE)
    schema = parser.introspect()

    assert schema.name == "fvavitao_identity"
    assert len(schema.tables) >= 18

    # Check key domain tables
    assert "membre" in schema.tables
    assert "fiangonana" in schema.tables
    assert "association" in schema.tables
    assert "cotisation" in schema.tables
    assert "membre_association" in schema.tables

    # Check primary keys
    assert schema.tables["membre"].primary_key == ["id"]
    assert schema.tables["membre_association"].primary_key == ["membre_id", "association_id"]

    # Check junction table detection
    assert schema.tables["membre_association"].is_junction is True
    assert schema.tables["evenement_note"].is_junction is True
    assert schema.tables["membre"].is_junction is False

    # Check foreign keys
    membre_fks = {fk.constrained_column: fk.referred_table for fk in schema.tables["membre"].foreign_keys}
    assert membre_fks["fiangonana_id"] == "fiangonana"
    assert membre_fks["zone_geographique_id"] == "groupe"


def test_schema_reverse_engine_generation():
    """Verify that SchemaReverseEngine produces expected entities, attributes and relationships."""
    parser = SQLDumpParser(SQL_FILE)
    schema = parser.introspect()

    engine = SchemaReverseEngine(schema, model_name="fvavitao_identity")
    manifest = engine.generate_manifest()

    assert "model" in manifest
    model = manifest["model"]
    assert model["name"] == "fvavitao_identity"

    entities = model["entities"]
    assert "Membre" in entities
    assert "Fiangonana" in entities
    assert "Association" in entities
    assert "Cotisation" in entities

    # Technical table messenger_messages should be excluded
    assert "MessengerMessages" not in entities

    # Junction table membre_association should be converted to M-N relationship
    assert "MembreAssociation" not in entities

    # Check Membre relationships
    membre = entities["Membre"]
    assert membre["storage"]["table"] == "membre"
    assert membre["storage"]["id"] == "id"

    # Forward Many-to-One
    assert "fiangonana" in membre["relationships"]
    assert membre["relationships"]["fiangonana"]["cardinality"] == "many-to-one"
    assert membre["relationships"]["fiangonana"]["target"] == "Fiangonana"

    # Many-to-Many through junction
    assert "associations" in membre["relationships"]
    assert membre["relationships"]["associations"]["cardinality"] == "many-to-many"
    assert membre["relationships"]["associations"]["through"] == "membre_association"
    assert membre["relationships"]["associations"]["target"] == "Association"

    # Inverse Many-to-Many on Association
    association = entities["Association"]
    assert "membres" in association["relationships"]
    assert association["relationships"]["membres"]["cardinality"] == "many-to-many"
    assert association["relationships"]["membres"]["through"] == "membre_association"
    assert association["relationships"]["membres"]["target"] == "Membre"


def test_introspect_sql_file_export(tmp_path):
    """Verify that introspect_sql_file writes a clean, valid YAML file."""
    output_path = tmp_path / "test_fvavitao.yaml"
    res = introspect_sql_file(SQL_FILE, output_yaml=output_path, model_name="test_model")

    assert output_path.is_file()
    assert res["model"]["name"] == "test_model"
    content = output_path.read_text(encoding="utf-8")
    assert "model:" in content
    assert "Fiangonana:" in content
    assert "Membre:" in content


def test_sql_dump_parser_handles_inline_and_composite_constraints():
    sql = """
    CREATE TABLE `team` (
        `id` INTEGER PRIMARY KEY,
        `label` VARCHAR(120) DEFAULT 'East, south'
    );
    CREATE TABLE `membership` (
        `team_id` INTEGER REFERENCES `team` (`id`),
        `member_id` INTEGER,
        PRIMARY KEY (`team_id`, `member_id`),
        CONSTRAINT `fk_member` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`)
    );
    """

    schema = SQLDumpParser(sql, schema_name="inline_schema").introspect()

    assert schema.name == "inline_schema"
    assert schema.tables["team"].primary_key == ["id"]
    assert schema.tables["team"].columns["id"].is_primary_key is True
    assert schema.tables["team"].columns["label"].sql_type == "varchar(120)"
    assert schema.tables["membership"].primary_key == ["team_id", "member_id"]
    assert schema.tables["membership"].is_junction is True
    assert {
        (fk.constrained_column, fk.referred_table, fk.referred_column)
        for fk in schema.tables["membership"].foreign_keys
    } == {
        ("team_id", "team", "id"),
        ("member_id", "member", "id"),
    }


def test_sql_dump_parser_handles_alter_table_constraints():
    sql = """
    CREATE TABLE parent (id INTEGER NOT NULL);
    CREATE TABLE child (id INTEGER NOT NULL, parent_id INTEGER NOT NULL);
    ALTER TABLE child ADD PRIMARY KEY (id);
    ALTER TABLE child
      ADD CONSTRAINT fk_child_parent FOREIGN KEY (parent_id) REFERENCES parent (id);
    """

    schema = SQLDumpParser(sql).introspect()
    child = schema.tables["child"]

    assert child.primary_key == ["id"]
    assert len(child.foreign_keys) == 1
    assert child.foreign_keys[0].constraint_name == "fk_child_parent"
    assert child.foreign_keys[0].referred_table == "parent"


def test_sql_dump_parser_rejects_plain_single_line_as_missing_file():
    with pytest.raises(FileNotFoundError, match="SQL dump file not found"):
        SQLDumpParser("not_a_sql_file.sql")


def test_cli_introspects_sql_file_and_exports_yaml(tmp_path):
    root = Path(__file__).resolve().parents[1]
    sql_file = tmp_path / "mini_schema.sql"
    output_file = tmp_path / "generated_model.yaml"
    sql_file.write_text(
        "CREATE TABLE `customer` (`id` INTEGER PRIMARY KEY, `name` VARCHAR(80));",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "axora.cli",
            "introspect",
            "--sql-file",
            str(sql_file),
            "--output",
            str(output_file),
        ],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Generated 1 semantic entities" in result.stdout
    assert "Customer:" in output_file.read_text(encoding="utf-8")
    from axora.semantic.service import SemanticModelService

    generated_model = SemanticModelService.from_yaml(output_file)
    assert generated_model.get_entity_names() == ["Customer"]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("postgresql+asyncpg://localhost/axora", "postgresql+psycopg://localhost/axora"),
        ("mysql+aiomysql://localhost/axora", "mysql+pymysql://localhost/axora"),
        ("mariadb+aiomysql://localhost/axora", "mysql+pymysql://localhost/axora"),
        ("sqlite+aiosqlite:///tmp/axora.db", "sqlite:///tmp/axora.db"),
    ],
)
def test_live_introspector_normalizes_sync_urls(source, expected):
    introspector = LiveDatabaseIntrospector(source)
    assert introspector._to_sync_url(source) == expected
