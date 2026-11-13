import logging
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from axora.extensions.bdd.sql.base import SQLBaseConnector
from axora.semantic.service import SemanticModelService

logger = logging.getLogger("axora.extensions.bdd.sql.mysql")


class MySQLConnector(SQLBaseConnector):
    """MySQL and MariaDB database connector utilizing aiomysql async driver."""

    def __init__(
        self,
        url: str,
        semantic_service: SemanticModelService | None = None,
        echo: bool = False,
        **engine_kwargs: Any,
    ) -> None:
        # Best practices for MySQL connections:
        # 1. pool_pre_ping: tests liveness before issuing queries
        # 2. pool_recycle: recycles connections before MySQL server wait_timeout (default 8h)
        engine_kwargs.setdefault("pool_pre_ping", True)
        engine_kwargs.setdefault("pool_recycle", 3600)

        super().__init__(url=url, semantic_service=semantic_service, echo=echo, **engine_kwargs)

    @property
    def dialect_name(self) -> str:
        return "mysql"

    def _normalize_url(self, url: str) -> str:
        """Converts mysql:// and mariadb:// URIs to mysql+aiomysql:// with utf8mb4 encoding."""
        clean = url.strip()

        # Handle scheme rewriting
        if clean.startswith("mysql://"):
            clean = clean.replace("mysql://", "mysql+aiomysql://", 1)
        elif clean.startswith("mariadb://"):
            clean = clean.replace("mariadb://", "mysql+aiomysql://", 1)
        elif clean.startswith("mariadb+aiomysql://"):
            clean = clean.replace("mariadb+aiomysql://", "mysql+aiomysql://", 1)

        # Ensure charset=utf8mb4 is set in query parameters
        try:
            parsed = urlparse(clean)
            query_params = parse_qs(parsed.query)
            if "charset" not in query_params:
                query_params["charset"] = ["utf8mb4"]
                new_query = urlencode(query_params, doseq=True)
                clean = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    new_query,
                    parsed.fragment,
                ))
        except Exception as exc:
            logger.debug(f"[MYSQL CONNECTOR] Failed to append charset to URL: {exc}")

        return clean

    async def connect(self) -> None:
        """Verifies driver availability and initializes the async engine."""
        try:
            import aiomysql  # noqa: F401
        except ImportError as exc:
            logger.warning(
                "[MYSQL CONNECTOR] 'aiomysql' package is not installed. "
                "Install it via 'pip install aiomysql' to connect to live MySQL instances."
            )

        await super().connect()
