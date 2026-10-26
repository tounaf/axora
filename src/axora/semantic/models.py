from typing import Literal
from pydantic import BaseModel, Field


class AttributeDefinition(BaseModel):
    column: str
    type: str
    description: str | None = None
    allowed_values: list[str] | None = None


class RelationshipDefinition(BaseModel):
    target: str
    cardinality: Literal["one-to-one", "one-to-many", "many-to-one", "many-to-many"]
    through: str | None = None


class StorageDefinition(BaseModel):
    table: str
    id: str = "id"


class EntityDefinition(BaseModel):
    description: str
    storage: StorageDefinition
    attributes: dict[str, AttributeDefinition] = Field(default_factory=dict)
    synonyms: list[str] = Field(default_factory=list)
    relationships: dict[str, RelationshipDefinition] = Field(default_factory=dict)
    standard_types: list[str] | None = None


class BusinessRuleDefinition(BaseModel):
    id: str
    description: str


class SemanticModel(BaseModel):
    name: str
    version: str
    description: str
    entities: dict[str, EntityDefinition]
    business_rules: list[BusinessRuleDefinition] = Field(default_factory=list)


class EntityOverview(BaseModel):
    name: str
    description: str
    synonyms: list[str]
