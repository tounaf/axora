from pathlib import Path
from axora.semantic.loader import load_semantic_model_from_yaml
from axora.semantic.models import (
    BusinessRuleDefinition,
    EntityDefinition,
    EntityOverview,
    SemanticModel,
)


class SemanticModelService:
    """Service providing query and inspection capabilities over a loaded SemanticModel."""

    def __init__(self, model: SemanticModel) -> None:
        self._model = model

    @classmethod
    def from_yaml(cls, file_path: str | Path) -> "SemanticModelService":
        model = load_semantic_model_from_yaml(file_path)
        return cls(model)

    @property
    def model_name(self) -> str:
        return self._model.name

    @property
    def version(self) -> str:
        return self._model.version

    def get_entities_overview(self) -> list[EntityOverview]:
        """Returns a summary list of all entities in the semantic model."""
        return [
            EntityOverview(
                name=name,
                description=entity.description,
                synonyms=entity.synonyms,
            )
            for name, entity in self._model.entities.items()
        ]

    def get_entity_names(self) -> list[str]:
        """Returns all entity names defined in the model."""
        return list(self._model.entities.keys())

    def get_entity_details(self, entity_name: str) -> EntityDefinition | None:
        """Retrieves detailed definition for a specific entity name, synonym, table, or variation.

        Returns None if entity is not found.
        """
        if not entity_name:
            return None

        # Direct lookup by entity name
        if entity_name in self._model.entities:
            return self._model.entities[entity_name]

        # Normalized lookup
        term = entity_name.lower().strip()

        # Build term variations (singular/plural, English/French common suffixes)
        variations = {term}
        if term.endswith("s"):
            variations.add(term[:-1])
        else:
            variations.add(f"{term}s")

        if term.startswith("member"):
            variations.update(["membre", "membres", "member", "members"])

        for name, entity in self._model.entities.items():
            candidate_terms = {name.lower(), entity.storage.table.lower()}
            for syn in entity.synonyms:
                syn_lower = syn.lower().strip()
                candidate_terms.add(syn_lower)
                if syn_lower.endswith("s"):
                    candidate_terms.add(syn_lower[:-1])
                else:
                    candidate_terms.add(f"{syn_lower}s")

            if variations & candidate_terms:
                return entity

        return None

    def get_business_rules(self) -> list[BusinessRuleDefinition]:
        """Returns all business rules declared in the semantic model."""
        return self._model.business_rules

    def resolve_concept_name(self, concept_query: str) -> str | None:
        """Resolves a raw concept query (name or synonym) to its canonical entity name."""
        entity = self.get_entity_details(concept_query)
        if not entity:
            return None
        for canonical_name, entity_def in self._model.entities.items():
            if entity_def is entity:
                return canonical_name
        return None
