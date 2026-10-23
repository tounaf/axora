from pathlib import Path
import pytest
from axora.semantic.loader import load_semantic_model_from_yaml
from axora.semantic.models import SemanticModel
from axora.semantic.service import SemanticModelService

YAML_PATH = Path("src/axora/semantic/definitions/gestion_paroissiale.yaml")


def test_load_semantic_model_valid():
    model = load_semantic_model_from_yaml(YAML_PATH)
    assert isinstance(model, SemanticModel)
    assert model.name == "gestion_paroissiale"
    assert "Membre" in model.entities
    assert "Paroisse" in model.entities


def test_load_semantic_model_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_semantic_model_from_yaml("invalid/path/non_existent.yaml")


def test_semantic_service_overview():
    service = SemanticModelService.from_yaml(YAML_PATH)
    overview = service.get_entities_overview()
    assert len(overview) >= 5
    names = [item.name for item in overview]
    assert "Membre" in names
    assert "ZoneGeographique" in names


def test_semantic_service_get_entity_details_direct():
    service = SemanticModelService.from_yaml(YAML_PATH)
    entity = service.get_entity_details("Membre")
    assert entity is not None
    assert entity.storage.table == "membre"
    assert "nom" in entity.attributes
    assert "sexe" in entity.attributes


def test_semantic_service_get_entity_details_synonym():
    service = SemanticModelService.from_yaml(YAML_PATH)
    # Synonym for Paroisse is 'église'
    entity = service.get_entity_details("église")
    assert entity is not None
    assert entity.storage.table == "paroisse"


def test_semantic_service_get_entity_details_non_existent():
    service = SemanticModelService.from_yaml(YAML_PATH)
    entity = service.get_entity_details("InexistantConcept")
    assert entity is None


def test_semantic_service_resolve_concept_name():
    service = SemanticModelService.from_yaml(YAML_PATH)
    assert service.resolve_concept_name("église") == "Paroisse"
    assert service.resolve_concept_name("Membre") == "Membre"
    assert service.resolve_concept_name("Inconnu") is None


def test_semantic_service_business_rules():
    service = SemanticModelService.from_yaml(YAML_PATH)
    rules = service.get_business_rules()
    assert len(rules) >= 5
    rule_ids = [r.id for r in rules]
    assert "BR-001" in rule_ids
    assert "BR-003" in rule_ids
