import pytest
from sqlalchemy import select
from sqlalchemy.dialects import mysql
from axora.data.dynamic_models import GUID, build_dynamic_tables, get_dynamic_table
from axora.extensions.bdd import MySQLConnector, connector_registry, get_connector
from axora.semantic.service import SemanticModelService

YAML_PATH = "src/axora/semantic/definitions/gestion_paroissiale.yaml"


@pytest.fixture
def semantic_service():
    return SemanticModelService.from_yaml(YAML_PATH)


def test_mysql_schemes_registered():
    """Verify all MySQL and MariaDB scheme variants are registered."""
    schemes = connector_registry.list_schemes()
    for expected in ("mysql", "mysql+aiomysql", "mysql+asyncmy", "mariadb", "mariadb+aiomysql"):
        assert expected in schemes, f"Scheme '{expected}' should be registered in connector_registry"

    conn_mysql = get_connector("mysql://root:secret@localhost:3306/axora")
    assert isinstance(conn_mysql, MySQLConnector)
    assert conn_mysql.dialect_name == "mysql"
    assert conn_mysql.is_nosql is False

    conn_mariadb = get_connector("mariadb://root:secret@localhost:3306/axora")
    assert isinstance(conn_mariadb, MySQLConnector)
    assert conn_mariadb.dialect_name == "mysql"


def test_mysql_url_normalization():
    """Verify standard URI rewriting to aiomysql async driver with utf8mb4 encoding."""
    connector = MySQLConnector("mysql://user:pass@localhost:3306/axora_db")
    normalized = connector._normalize_url(connector.raw_url)
    assert normalized.startswith("mysql+aiomysql://user:pass@localhost:3306/axora_db")
    assert "charset=utf8mb4" in normalized

    # MariaDB scheme normalization
    connector_maria = MySQLConnector("mariadb://user:pass@host:3307/maria_db")
    normalized_maria = connector_maria._normalize_url(connector_maria.raw_url)
    assert normalized_maria.startswith("mysql+aiomysql://user:pass@host:3307/maria_db")
    assert "charset=utf8mb4" in normalized_maria


def test_mysql_engine_defaults():
    """Verify MySQL engine kwargs: pool_pre_ping and pool_recycle."""
    connector = MySQLConnector("mysql://localhost/test")
    assert connector._engine_kwargs.get("pool_pre_ping") is True
    assert connector._engine_kwargs.get("pool_recycle") == 3600


def test_mysql_safe_log_url():
    """Verify credentials masking for secure observability."""
    connector = MySQLConnector("mysql://admin:super_secret_pwd@127.0.0.1:3306/prod_db")
    safe = connector._safe_log_url(connector.raw_url)
    assert "super_secret_pwd" not in safe
    assert "admin:****@127.0.0.1:3306/prod_db" in safe


def test_mysql_dialect_guid_transposition(semantic_service):
    """Verify that GUID types automatically compile to CHAR(36) in MySQL dialect."""
    mysql_dialect = mysql.dialect()
    guid_type = GUID()

    # In MySQL, GUID must be CHAR(36)
    compiled_type = guid_type.compile(dialect=mysql_dialect)
    assert "CHAR(36)" in str(compiled_type).upper()


def test_mysql_query_compilation_with_backticks(semantic_service):
    """Verify that dynamic tables generate valid MySQL syntax with backticks."""
    build_dynamic_tables(semantic_service)
    table_membre = get_dynamic_table("membre", semantic_service)
    assert table_membre is not None

    stmt = select(table_membre).where(table_membre.c.nom == "Rabe")
    compiled_sql = str(stmt.compile(dialect=mysql.dialect()))

    # MySQL dialect wraps tables and columns in backticks
    assert "`membre`" in compiled_sql
    assert "`nom`" in compiled_sql
    assert "SELECT" in compiled_sql
    assert "WHERE" in compiled_sql
