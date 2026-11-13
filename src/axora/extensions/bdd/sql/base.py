import logging
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from axora.data.dynamic_models import build_dynamic_tables
from axora.data.mutation_engine import MutationEngine
from axora.data.query_engine import QueryEngine
from axora.extensions.bdd.interface import DatabaseConnectorInterface
from axora.semantic.models import EntityDefinition
from axora.semantic.service import SemanticModelService

logger = logging.getLogger("axora.extensions.bdd.sql.base")


class SQLBaseConnector(DatabaseConnectorInterface):
    """Generic base connector for relational SQL databases utilizing SQLAlchemy Async."""

    def __init__(
        self,
        url: str,
        semantic_service: SemanticModelService | None = None,
        echo: bool = False,
        **engine_kwargs: Any,
    ) -> None:
        self.raw_url = url
        self.semantic_service = semantic_service
        self._echo = echo
        self._engine_kwargs = engine_kwargs
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._query_engine: QueryEngine | None = None
        self._mutation_engine: MutationEngine | None = None

    @property
    def is_nosql(self) -> bool:
        return False

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("DatabaseConnector is not connected. Call 'await connect()' first.")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            raise RuntimeError("DatabaseConnector is not connected. Call 'await connect()' first.")
        return self._session_factory

    def _normalize_url(self, url: str) -> str:
        """Subclasses can override to adjust dialect or async driver prefix."""
        return url

    async def connect(self) -> None:
        """Initializes the SQLAlchemy async engine and session factory."""
        if self._engine is not None:
            return

        normalized_url = self._normalize_url(self.raw_url)
        logger.info(f"[{self.dialect_name.upper()} CONNECTOR] Initializing async engine for: {self._safe_log_url(normalized_url)}")

        self._engine = create_async_engine(
            normalized_url,
            echo=self._echo,
            future=True,
            **self._engine_kwargs,
        )

        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        if self.semantic_service:
            build_dynamic_tables(self.semantic_service)
            self._query_engine = QueryEngine(self.semantic_service)
            self._mutation_engine = MutationEngine(self.semantic_service)

    async def disconnect(self) -> None:
        """Disposes the async engine pool and clears active factories."""
        if self._engine is not None:
            logger.info(f"[{self.dialect_name.upper()} CONNECTOR] Disposing engine pool...")
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def health_check(self) -> dict[str, Any]:
        """Runs a lightweight ping query (SELECT 1) and measures response latency."""
        start_time = time.perf_counter()
        try:
            if self._engine is None:
                await self.connect()

            async with self.session_scope() as session:
                res = await session.execute(text("SELECT 1"))
                res.scalar()

            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "ok",
                "dialect": self.dialect_name,
                "latency_ms": latency_ms,
                "is_nosql": self.is_nosql,
            }
        except Exception as exc:
            logger.error(f"[{self.dialect_name.upper()} CONNECTOR HEALTHCHECK ERROR] {exc}")
            return {
                "status": "error",
                "dialect": self.dialect_name,
                "error": str(exc),
                "is_nosql": self.is_nosql,
            }

    @asynccontextmanager
    async def session_scope(self) -> AsyncGenerator[AsyncSession, None]:
        """Provides an async transactional session context."""
        if self._session_factory is None:
            await self.connect()
        assert self._session_factory is not None

        async with self._session_factory() as session:
            yield session

    async def init_schema(self) -> None:
        """Creates tables dynamically in the target database based on registered models."""
        if self._engine is None:
            await self.connect()
        assert self._engine is not None

        from axora.data.dynamic_models import metadata
        async with self._engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def execute_query(
        self,
        entity_def: EntityDefinition,
        select_fields: list[str] | None = None,
        filters: list[dict[str, Any]] | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Executes a structured semantic query via the integrated QueryEngine."""
        if not self._query_engine:
            if not self.semantic_service:
                raise ValueError("Cannot execute semantic query: no SemanticModelService provided.")
            self._query_engine = QueryEngine(self.semantic_service)

        async with self.session_scope() as session:
            return await self._query_engine.execute_query(
                session=session,
                entity_name=entity_def.name,
                select_fields=select_fields,
                filters=filters,
                limit=limit,
            )

    async def execute_mutation(
        self,
        entity_def: EntityDefinition,
        action: str,
        payload: dict[str, Any],
        record_id: Any | None = None,
    ) -> dict[str, Any]:
        """Executes a create or update mutation via the integrated MutationEngine."""
        if not self._mutation_engine:
            if not self.semantic_service:
                raise ValueError("Cannot execute semantic mutation: no SemanticModelService provided.")
            self._mutation_engine = MutationEngine(self.semantic_service)

        async with self.session_scope() as session:
            async with session.begin():
                if action == "create":
                    return await self._mutation_engine.create_record(
                        session=session,
                        entity_name=entity_def.name,
                        payload=payload,
                    )
                elif action == "update":
                    if record_id is None:
                        raise ValueError(f"Action 'update' on entity '{entity_def.name}' requires a 'record_id'.")
                    return await self._mutation_engine.update_record(
                        session=session,
                        entity_name=entity_def.name,
                        record_id=record_id,
                        payload=payload,
                    )
                else:
                    raise ValueError(f"Unsupported mutation action: '{action}'. Expected 'create' or 'update'.")

    def _safe_log_url(self, url: str) -> str:
        """Masks passwords in database connection strings for safe logging."""
        if "@" in url and "://" in url:
            prefix, rest = url.split("://", 1)
            creds, host_part = rest.split("@", 1)
            if ":" in creds:
                user = creds.split(":", 1)[0]
                return f"{prefix}://{user}:****@{host_part}"
        return url
