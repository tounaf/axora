from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from axora.semantic.models import EntityDefinition
else:
    EntityDefinition = Any


class DatabaseConnectorInterface(ABC):
    """Universal interface for Axora database connectors (SQL & NoSQL)."""

    @property
    @abstractmethod
    def dialect_name(self) -> str:
        """Name of the dialect (e.g. 'postgresql', 'sqlite', 'mysql', 'mongodb', 'mssql', 'oracle')."""
        pass

    @property
    @abstractmethod
    def is_nosql(self) -> bool:
        """True if the connector targets a NoSQL/document-oriented database, False for relational SQL."""
        pass

    @abstractmethod
    async def connect(self) -> None:
        """Initializes the connection pool or client asynchronously."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully closes all open connections and disposes resources."""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Performs a ping or lightweight query to verify connectivity and latency."""
        pass

    @abstractmethod
    async def execute_query(
        self,
        entity_def: EntityDefinition,
        select_fields: list[str] | None = None,
        filters: list[dict[str, Any]] | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Executes an abstract semantic query and returns normalized dictionary records."""
        pass

    @abstractmethod
    async def execute_mutation(
        self,
        entity_def: EntityDefinition,
        action: str,  # 'create', 'update', 'delete'
        payload: dict[str, Any],
        record_id: Any | None = None,
    ) -> dict[str, Any]:
        """Executes a create, update or delete operation with semantic business rule validation."""
        pass
