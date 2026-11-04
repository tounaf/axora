from abc import ABC, abstractmethod
from typing import Any, Literal
from pydantic import BaseModel, Field


class ColumnMetadata(BaseModel):
    key: str
    label: str
    data_type: Literal["string", "number", "date", "badge", "tags", "boolean"] = "string"
    sortable: bool = True


class ViewPayload(BaseModel):
    """Structured, domain-agnostic view contract payload returned to frontends."""

    view_type: str  # e.g., 'table', 'chart', 'metric_cards', 'network_graph'
    title: str
    description: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class ViewBuilderInterface(ABC):
    """Interface for extensible view builders."""

    @property
    @abstractmethod
    def view_type(self) -> str:
        """Unique identifier of the view type (e.g. 'table', 'chart')."""
        pass

    @abstractmethod
    def build(self, data: Any, **kwargs: Any) -> ViewPayload:
        """Transforms arbitrary business data into a valid ViewPayload."""
        pass
