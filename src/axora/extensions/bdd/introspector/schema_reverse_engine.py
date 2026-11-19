from pathlib import Path
from typing import Any
import yaml
from axora.extensions.bdd.introspector.interface import DatabaseSchema, TableInfo


class SchemaReverseEngine:
    """Transforms raw database schema metadata into an Axora Semantic Model manifest (YAML)."""

    TECHNICAL_TABLES = {"messenger_messages", "doctrine_migration_versions", "alembic_version"}

    SYNONYM_DICTIONARY = {
        "fiangonana": ["paroisse", "eglise", "communaute"],
        "groupe": ["zone", "zone_geographique", "secteur", "quartier"],
        "membre": ["adherent", "fidele", "personne", "chretien"],
        "association": ["sampana", "groupe_activite", "organisation"],
        "sous_groupe": ["branche", "sous_section", "comite"],
        "cotisation": ["adhesion", "paiement", "contribution"],
        "don": ["offrande", "dime", "donation", "aide"],
        "evenement": ["culte", "reunion", "programme", "activite"],
        "presence": ["pointage", "assiduite", "participation"],
        "type_evenement": ["categorie_evenement", "nature_evenement"],
        "role": ["fonction", "titre", "responsabilite"],
        "permission": ["droit", "autorisation"],
        "note": ["remarque", "compte_rendu", "observation"],
        "media": ["fichier", "photo", "document", "piece_jointe"],
    }

    ENTITY_DESCRIPTIONS = {
        "fiangonana": "Paroisse ou communauté ecclésiale locale.",
        "groupe": "Zone géographique ou groupe de quartier rattaché à une paroisse.",
        "membre": "Personne ou fidèle membre de la communauté paroissiale.",
        "association": "Association ou groupe d'activité paroissial (ex. Hommes, Femmes, Jeunes).",
        "sous_groupe": "Sous-groupe spécialisé opérant au sein d'une association.",
        "cotisation": "Cotisation ou droit d'adhésion versé par un membre.",
        "don": "Don financier ou matériel offert à la communauté.",
        "evenement": "Culte, assemblée ou événement organisé par la communauté.",
        "type_evenement": "Type ou catégorie d'événement (ex: Culte dominical, Conférence).",
        "presence": "Enregistrement de présence ou émargement à une activité.",
        "role": "Rôle de sécurité ou mandat organisationnel au sein de la paroisse.",
        "permission": "Droit d'accès accordé à un rôle sur une fonctionnalité.",
        "feature": "Fonctionnalité ou module applicatif soumis à habilitation.",
        "role_assignment": "Attribution d'un rôle à un membre dans un contexte spécifique.",
        "note": "Note textuelle ou compte-rendu associé à un événement.",
        "media": "Ressource multimédia (photo, document) liée à un événement.",
    }

    def __init__(self, schema: DatabaseSchema, model_name: str | None = None) -> None:
        self.schema = schema
        self.model_name = model_name or schema.name

    def to_pascal_case(self, name: str) -> str:
        """Converts snake_case or table_name to PascalCase entity identifier."""
        return "".join(part.capitalize() for part in name.split("_"))

    def pluralize(self, name: str) -> str:
        """Simple pluralizer for reverse relationships."""
        if name.endswith("s") or name.endswith("x"):
            return name
        return f"{name}s"

    def generate_manifest(self) -> dict[str, Any]:
        """Generates the full dictionary structure compliant with SemanticModel schema."""
        entities: dict[str, Any] = {}

        # 1. Filter out technical tables and junction tables from primary entities
        domain_tables = {
            t_name: tbl for t_name, tbl in self.schema.tables.items()
            if t_name not in self.TECHNICAL_TABLES and not tbl.is_junction
        }

        junction_tables = {
            t_name: tbl for t_name, tbl in self.schema.tables.items()
            if tbl.is_junction and t_name not in self.TECHNICAL_TABLES
        }

        # 2. Build base entity definitions
        for tbl_name, tbl in domain_tables.items():
            entity_name = self.to_pascal_case(tbl_name)
            pk_col = tbl.primary_key[0] if tbl.primary_key else "id"

            attributes: dict[str, Any] = {}
            for col_name, col in tbl.columns.items():
                if col_name == pk_col:
                    continue  # PK handled in storage.id

                attr_dict: dict[str, Any] = {
                    "column": col_name,
                    "type": col.semantic_type,
                    "description": col.comment or f"Attribut {col_name} de {entity_name}",
                }

                # Auto-detect allowed values for gender or status columns
                if col_name.lower() in ("sexe", "gender"):
                    attr_dict["allowed_values"] = ["HOMME", "FEMME"]
                elif col_name.lower() in ("statut", "status"):
                    attr_dict["allowed_values"] = ["ACTIF", "INACTIF", "EN_ATTENTE"]

                attributes[col_name] = attr_dict

            relationships: dict[str, Any] = {}

            # Forward relationships: Many-to-One
            for fk in tbl.foreign_keys:
                if fk.referred_table in self.schema.tables and fk.referred_table not in self.TECHNICAL_TABLES:
                    target_entity = self.to_pascal_case(fk.referred_table)
                    rel_name = fk.constrained_column.replace("_id", "")
                    # Ensure unique relationship key
                    if rel_name in relationships:
                        rel_name = f"{rel_name}_{target_entity.lower()}"

                    relationships[rel_name] = {
                        "target": target_entity,
                        "cardinality": "many-to-one",
                    }

            synonyms = list(self.SYNONYM_DICTIONARY.get(tbl_name, [tbl_name.lower()]))
            description = self.ENTITY_DESCRIPTIONS.get(
                tbl_name,
                f"Entité métier canonique issue de la table {tbl_name}.",
            )

            entities[entity_name] = {
                "description": description,
                "storage": {
                    "table": tbl_name,
                    "id": pk_col,
                },
                "attributes": attributes,
                "synonyms": synonyms,
                "relationships": relationships,
            }

        # 3. Add reverse One-to-Many relationships
        for tbl_name, tbl in domain_tables.items():
            source_entity = self.to_pascal_case(tbl_name)
            for fk in tbl.foreign_keys:
                target_table = fk.referred_table
                target_entity = self.to_pascal_case(target_table)

                if target_entity in entities:
                    rev_rel_name = self.pluralize(tbl_name)
                    # If multiple FKs point to same table (e.g. membre_id and scanned_by_id)
                    fk_col_clean = fk.constrained_column.replace("_id", "")
                    if rev_rel_name in entities[target_entity]["relationships"]:
                        rev_rel_name = f"{rev_rel_name}_via_{fk_col_clean}"

                    entities[target_entity]["relationships"][rev_rel_name] = {
                        "target": source_entity,
                        "cardinality": "one-to-many",
                    }

        # 4. Add Many-to-Many relationships from Junction tables
        for j_name, j_tbl in junction_tables.items():
            if len(j_tbl.foreign_keys) == 2:
                fk1, fk2 = j_tbl.foreign_keys[0], j_tbl.foreign_keys[1]
                t1, t2 = fk1.referred_table, fk2.referred_table
                e1, e2 = self.to_pascal_case(t1), self.to_pascal_case(t2)

                if e1 in entities and e2 in entities:
                    # e1 -> e2
                    rel1 = self.pluralize(t2)
                    entities[e1]["relationships"][rel1] = {
                        "target": e2,
                        "cardinality": "many-to-many",
                        "through": j_name,
                    }
                    # e2 -> e1
                    rel2 = self.pluralize(t1)
                    entities[e2]["relationships"][rel2] = {
                        "target": e1,
                        "cardinality": "many-to-many",
                        "through": j_name,
                    }

        return {
            "model": {
                "name": self.model_name,
                "version": "1.0",
                "description": f"Modèle sémantique généré automatiquement à partir de la base {self.schema.name}.",
                "entities": entities,
                "business_rules": [
                    {
                        "id": "BR-AUTO-001",
                        "description": "L'intégrité référentielle des clés étrangères doit être respectée lors de toute création ou mise à jour.",
                    }
                ],
            }
        }

    def export_yaml(self, output_path: str | Path) -> Path:
        """Writes the generated semantic model into a formatted YAML file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        manifest_dict = self.generate_manifest()

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(manifest_dict, f, allow_unicode=True, sort_keys=False, indent=2)

        return path
