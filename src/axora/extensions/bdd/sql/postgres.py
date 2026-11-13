from typing import Any
from axora.extensions.bdd.sql.base import SQLBaseConnector
from axora.semantic.service import SemanticModelService


class PostgresConnector(SQLBaseConnector):
    """PostgreSQL database connector utilizing psycopg3 async driver."""

    def __init__(
        self,
        url: str,
        semantic_service: SemanticModelService | None = None,
        echo: bool = False,
        **engine_kwargs: Any,
    ) -> None:
        engine_kwargs.setdefault("pool_pre_ping", True)
        super().__init__(url=url, semantic_service=semantic_service, echo=echo, **engine_kwargs)

    @property
    def dialect_name(self) -> str:
        return "postgresql"

    def _normalize_url(self, url: str) -> str:
        """Converts default postgresql:// URI to postgresql+psycopg:// for async execution."""
        clean = url.strip()
        if clean.startswith("postgresql://"):
            return clean.replace("postgresql://", "postgresql+psycopg://", 1)
        return clean
