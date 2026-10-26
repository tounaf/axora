# Axora — FEAT-06 : Spécifications & Documentation Technique du Moteur de Mutation (`MutationEngine`), `create_record` et `update_record`

**Version :** 1.1
**Statut :** Documentation technique détaillée de FEAT-06
**Composants :** `src/axora/data/mutation_engine.py`, `src/axora/tools/create_record.py`, `src/axora/tools/update_record.py`

---

## 1. Présentation de FEAT-06

FEAT-06 dote l agent Axora de la capacité d **exécuter des créations et mises à jour de données métier de manière contrôlée et sécurisée**.

Elle comprend :
1. **Le moteur de mutation `MutationEngine`** qui gère la création (`create_record`) et la mise à jour (`update_record`) d entités ORM.
2. **La validation stricte des règles métier du domaine** (ex: vérification de l appartenance de la zone à la paroisse, validation du sexe `HOMME`/`FEMME`, validation du statut matrimonial `CELIBATAIRE`/`MARIE`).
3. **Les outils agentiques `create_record` et `update_record`** exposés au `ToolRegistry`.
4. **La conversion automatique des types** (changement des chaînes ISO en `datetime.date` et des GUID texte en `uuid.UUID`).

---

## 2. Architecture & Composants

```text
src/axora/data/
├── mutation_engine.py   # BusinessRuleViolation & MutationEngine
src/axora/tools/
├── create_record.py     # Outil agentique create_record
└── update_record.py     # Outil agentique update_record
```

---

## 3. Diagramme de Flux de Traitement d une Mutation

```mermaid
flowchart TD
    LLM[Agent LLM] --> CallTool[Appel de create_record / update_record]
    CallTool --> ValidateParams[Validation de la structure des arguments]
    ValidateParams --> Engine[MutationEngine]
    Engine --> TypeConvert[Conversion des chaînes ISO vers UUID / date]
    TypeConvert --> ValidateRules{Validation des Règles Métier<br/>(ex: BR-001 Zone-Paroisse, BR-002 Sexe/Statut)}

    ValidateRules -- Non respecté --> Exception[Lever BusinessRuleViolation]
    Exception --> ToolError[Retourner ToolResult status=error<br/>error_code=BUSINESS_RULE_VIOLATION]

    ValidateRules -- Valide --> DBExec[Exécuter l insertion / mise à jour dans PostgreSQL]
    DBExec --> CommitTx[Commit de la Transaction Atomique]
    CommitTx --> Success[Retourner ToolResult status=success<br/>avec le record créé/modifié]
```

---

## 4. Contrats JSON des Outils de Mutation

### Outil `create_record`

```json
{
  "name": "create_record",
  "arguments": {
    "entity": "Membre",
    "payload": {
      "paroisse_id": "ad47c7dc-3325-4809-beb4-67edc81b3e60",
      "zone_geographique_id": "ad47c7dc-3325-4809-beb4-67edc81b3e61",
      "nom": "Rakoto",
      "prenom": "Jean",
      "sexe": "HOMME",
      "date_naissance": "1990-01-01",
      "statut_matrimonial": "MARIE"
    }
  }
}
```

### Outil `update_record`

```json
{
  "name": "update_record",
  "arguments": {
    "entity": "Membre",
    "record_id": "550e8400-e29b-41d4-a716-446655440000",
    "payload": {
      "statut_matrimonial": "MARIE"
    }
  }
}
```

---

## 5. Exemples de Gestion des Erreurs Métier

Si l agent tente de créer un membre rattaché à une zone n appartenant pas à sa paroisse :

**Réponse de l outil (`ToolResult`) :**
```json
{
  "status": "error",
  "error_code": "BUSINESS_RULE_VIOLATION",
  "message": "BR-001: La zone géographique ad47c7dc-... n appartient pas à la paroisse ad47c7dc-....",
  "data": null
}
```

L agent reçoit cette erreur comme observation et peut formuler une réponse d explication claire ou demander des précisions à l utilisateur.

---

## 6. Validation par les Tests Unitaires

La suite de tests dans `tests/test_mutation_engine.py` couvre :
1. Création réussie d un membre avec types valides.
2. Invalidation automatique en cas d inadéquation entre la paroisse et la zone géographiques (`BR-001`).
3. Exécution complète de l outil `create_record`.
4. Exécution complète de l outil `update_record`.

**Commande d exécution :**
```bash
PYTHONPATH=src python3 -m pytest tests/test_mutation_engine.py
```

---

**Axora — From intent to action.**
