from typing import TYPE_CHECKING, Any
from axora.extensions.bdd.interface import DatabaseConnectorInterface
from axora.extensions.bdd.registry import ConnectorRegistry
from axora.extensions.bdd.sql.base import SQLBaseConnector
from axora.extensions.bdd.sql.mysql import MySQLConnector
from axora.extensions.bdd.sql.postgres import PostgresConnector
from axora.extensions.bdd.sql.sqlite import SqliteConnector

if TYPE_CHECKING:
    from axora.semantic.service import SemanticModelService
else:
    SemanticModelService = Any

# Global connector registry instance
connector_registry = ConnectorRegistry()

# Register core SQL drivers for Jalon 1 (Postgres, SQLite) and Jalon 2 (MySQL, MariaDB)
connector_registry.register("postgresql", PostgresConnector)
connector_registry.register("postgresql+psycopg", PostgresConnector)
connector_registry.register("postgresql+asyncpg", PostgresConnector)
connector_registry.register("sqlite", SqliteConnector)
connector_registry.register("sqlite+aiosqlite", SqliteConnector)
connector_registry.register("mysql", MySQLConnector)
connector_registry.register("mysql+aiomysql", MySQLConnector)
connector_registry.register("mysql+asyncmy", MySQLConnector)
connector_registry.register("mariadb", MySQLConnector)
connector_registry.register("mariadb+aiomysql", MySQLConnector)


def get_connector(
    url: str | None = None,
    semantic_service: SemanticModelService | None = None,
    **kwargs: Any,
) -> DatabaseConnectorInterface:
    """Factory helper returning a configured database connector based on connection URL."""
    if url is None:
        try:
            from axora.config import settings
            target_url = settings.DATABASE_URL
        except Exception:
            target_url = "sqlite+aiosqlite:///:memory:"
    else:
        target_url = url
    return connector_registry.create(url=target_url, semantic_service=semantic_service, **kwargs)


__all__ = [
    "DatabaseConnectorInterface",
    "ConnectorRegistry",
    "SQLBaseConnector",
    "PostgresConnector",
    "SqliteConnector",
    "MySQLConnector",
    "connector_registry",
    "get_connector",
]
