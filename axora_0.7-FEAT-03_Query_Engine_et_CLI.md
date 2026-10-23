# Axora — FEAT-03 : Spécifications & Documentation Technique du Moteur de Requête (`query_data`), Configuration des Tokens LLM et Interface CLI

**Version :** 0.7
**Statut :** Spécifications et guide de démarrage local CLI
**Composants :** `src/axora/data/` (`models.py`, `database.py`, `query_engine.py`), `src/axora/tools/query_data.py`, `src/axora/cli.py`

---

## 1. Présentation de FEAT-03

FEAT-03 apporte à l meagent Axora la capacité d exécution de requêtes de consultation de données de manière **sécurisée, dynamique et paramétrée**.

Elle comprend :
1. **Les modèles ORM SQLAlchemy 2.0 Async** reflétant le modèle relationnel.
2. **Le moteur de requêtes `QueryEngine`** qui traduit les chemins sémantiques (ex: `paroisse.nom`, `zone.nom`) en jointures et filtres SQL paramétrés sans aucun risque d injection SQL.
3. **L outil agentique `query_data`** qui expose cette capacité à l agent sous forme de contrat JSON.
4. **La configuration des jetons (tokens) LLM externes** via des variables d environnement centralisées.
5. **L interface utilisateur Terminal CLI (`src/axora/cli.py`)** permettant de communiquer interactivement avec l agent pour des tests fonctionnels en local.

---

## 2. Configuration des Jetons (Tokens) LLM Externe

La configuration des fournisseurs de modèles de langage (OpenAI, Anthropic, Ollama) s effectue via le fichier `.env`.

### Modèle de fichier `.env` :

```env
# Configuration LLM Externe
LLM_PROVIDER=openai              # Fournisseur: openai, anthropic, ollama, mock
LLM_API_KEY=sk-proj-your-api-key # Votre clé API officielle
LLM_MODEL=gpt-4o-mini            # Modèle cible
LLM_TEMPERATURE=0.0              # Température déterministe (0.0 conseillé)
```

Toutes les clés sont chargées de manière sécurisée et typée par Pydantic Settings dans `src/axora/config.py`.

---

## 3. Architecture et Moteur de Requête (`query_data`)

### Diagramme de Flux du Moteur de Requête

```mermaid
flowchart TD
    LLM[Agent LLM / Utilisateur CLI] --> QueryTool[Outil query_data]
    QueryTool --> ValidateJSON[Validation des arguments JSON]
    ValidateJSON --> Engine[QueryEngine.execute_query]
    Engine --> ResolveEntity[Résolution du nom canonique via SemanticModelService]
    ResolveEntity --> BuildStmt[Construction de la clause select SQLAlchemy]
    BuildStmt --> JoinPath{Analyse des chemins de filtres<br/>ex: paroisse.nom}

    JoinPath -- Chemin relationnel --> ApplyJoin[Ajout dynamique de la jointure join()]
    JoinPath -- Champ direct --> ApplyWhere[Ajout de la condition .where()]
    ApplyJoin --> ApplyWhere

    ApplyWhere --> ExecQuery[Exécution asynchrone sur la DB]
    ExecQuery --> FormatRows[Formatage des enregistrements en dictionnaires Python]
    FormatRows --> ReturnResult([Renvoyer ToolResult au Runtime Agent])
```

---

## 4. Interface Interactive Terminal CLI

L interface CLI permet de communiquer directement avec l agent Axora depuis votre terminal.

### Lancement du CLI en Local (Hors Docker) :

```bash
# 1. Activer votre environnement virtuel Python
source .venv/bin/activate  # ou venv/bin/activate

# 2. Exécuter le CLI Axora
PYTHONPATH=src python3 -m axora.cli
```

### Lancement du CLI via Docker Compose :

```bash
docker compose exec api python -m axora.cli
```

---

## 5. Validation par les Tests Unitaires

La suite de tests unitaires et d intégration dans `tests/test_query_engine.py` valide :
1. Les requêtes directes sur une entité (`Membre`).
2. La résolution dynamique des chemins relationnels (`paroisse.nom`, `zone.nom`).
3. L exécution complète de l outil `query_data`.

**Commande d exécution :**
```bash
PYTHONPATH=src python3 -m pytest tests/test_query_engine.py
```

---

**Axora — From intent to action.**
