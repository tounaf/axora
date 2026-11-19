from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ColumnInfo:
    name: str
    sql_type: str
    semantic_type: str  # 'string', 'number', 'date', 'boolean', 'text'
    is_nullable: bool = True
    is_primary_key: bool = False
    comment: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ForeignKeyInfo:
    constrained_column: str
    referred_table: str
    referred_column: str
    constraint_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TableInfo:
    name: str
    columns: dict[str, ColumnInfo] = field(default_factory=dict)
    primary_key: list[str] = field(default_factory=list)
    foreign_keys: list[ForeignKeyInfo] = field(default_factory=list)
    is_junction: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DatabaseSchema:
    name: str
    tables: dict[str, TableInfo] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SchemaIntrospectorInterface(ABC):
    """Abstract interface for database and schema dump introspectors."""

    @abstractmethod
    def introspect(self) -> DatabaseSchema:
        """Extracts tables, columns, primary keys and foreign keys."""
        pass
