from __future__ import annotations

from typing import TYPE_CHECKING, Any
from axora.extensions.bdd.sql.base import SQLBaseConnector

if TYPE_CHECKING:
    from axora.semantic.service import SemanticModelService
else:
    SemanticModelService = Any


class SqliteConnector(SQLBaseConnector):
    """SQLite database connector utilizing aiosqlite async driver."""

    def __init__(
        self,
        url: str,
        semantic_service: SemanticModelService | None = None,
        echo: bool = False,
        **engine_kwargs: Any,
    ) -> None:
        normalized = self._normalize_url(url)
        if ":memory:" in normalized or normalized.endswith(":memory:"):
            from sqlalchemy.pool import StaticPool
            engine_kwargs.setdefault("connect_args", {"check_same_thread": False})
            engine_kwargs.setdefault("poolclass", StaticPool)

        super().__init__(url=url, semantic_service=semantic_service, echo=echo, **engine_kwargs)

    @property
    def dialect_name(self) -> str:
        return "sqlite"

    def _normalize_url(self, url: str) -> str:
        """Converts default sqlite:// URI to sqlite+aiosqlite:// for async execution."""
        clean = url.strip()
        if clean.startswith("sqlite://") and not clean.startswith("sqlite+aiosqlite://"):
            return clean.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return clean
