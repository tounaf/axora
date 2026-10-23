# Axora — Règles et Bonnes Pratiques de Développement

Ce document définit les normes, conventions et bonnes pratiques obligatoires pour toute contribution au projet **Axora**. Chaque développeur et contributeur (humain ou agent IA) doit s'y conformer.

---

## 1. Principes d'Ingénierie & Philosophie Axora

1. **Agent-Centric & Deterministic Execution :**
   - L'Agent IA interprète l'intention et propose des décisions structurées.
   - Le Runtime Python orchestre, contrôle la boucle, et exécute les outils de façon déterministe.
2. **Aucune Exécution SQL Brute par le LLM :**
   - Le LLM ne doit **jamais** écrire ou exécuter du SQL direct.
   - Il utilise l'outil générique `query_data` qui génère des requêtes SQLAlchemy paramétrées et sécurisées.
3. **Validation Stricte par Pydantic :**
   - Toutes les entrées, sorties d'outils et décisions de l'agent doivent passer par la validation de modèles Pydantic v2.
4. **Indépendance vis-à-vis du Fournisseur LLM :**
   - Tout appel LLM est encapsulé derrière un adaptateur (`LLMAdapter`). Aucune dépendance directe à une SDK propriétaire ne doit fuiter hors du module `src/axora/llm/`.
5. **Modèle Sémantique Explicite :**
   - Les règles métier et structures de données sont découvertes via le `SemanticModelService` plutôt que supposées par le LLM.

---

## 2. Standards de Code Python

- **Version Python :** Python 3.12+
- **Style de Code :** Conforme à **PEP 8**.
- **Typage Statique Obligatoire :** Utiliser les annotations de type Python (`type hints`) systématiquement sur toutes les fonctions et méthodes public/private.
  ```python
  async def get_entity_details(entity_name: str) -> EntityDefinition | None:
      ...
  ```
- **Gestion des Erreurs :**
  - Ne jamais utiliser de `except Exception: pass` silencieux.
  - Intercepter les exceptions spécifiques et renvoyer des erreurs structurées (`ToolResult` avec `status="error"` et `message`).
- **Code Asynchrone :**
  - Utiliser `async`/`await` pour toutes les opérations d'I/O (FastAPI, SQLAlchemy AsyncEngine, appels API LLM, exécution d'outils).

---

## 3. Workflow Git & Commits

- **Branches :**
  - `main` : Branche stable de production.
  - Feature branches : Naming convention `feature/<nom-court>` ou `fix/<nom-court>`.
- **Messages de Commit :**
  - Respecter le format Conventional Commits :
    - `feat: ...` pour une nouvelle fonctionnalité.
    - `fix: ...` pour une correction de bug.
    - `docs: ...` pour la documentation.
    - `test: ...` pour l'ajout/modification de tests.
    - `refactor: ...` pour la restructuration de code.
  - Exemple : `feat(agent): implement bounded execution loop with pydantic validation`

---

## 4. Stratégie de Test & Qualité

- **Framework :** `pytest` et `pytest-asyncio`.
- **Exigence de Test :**
  - Tout nouvel outil ou composant agentique doit être accompagné d'un test unitaire ou d'intégration.
  - Les scénarios métier (ex: requêtes paroissiales) doivent vérifier les résultats retournés par rapport à un jeu de données connu.
- **Commande d'exécution des tests :**
  ```bash
  docker compose exec api pytest
  # Ou localement si l'environnement virtuel est activé :
  pytest
  ```

---

## 5. Sécurité et Gestion des Secrets

- **Fichiers de configuration :**
  - Ne **jamais** commiter de clés API, mots de passe ou secrets dans le dépôt Git.
  - Utiliser le fichier `.env` (dérivé de `.env.example`).
  - Toutes les variables d'environnement sont centralisées dans `src/axora/config.py` via Pydantic `BaseSettings`.

---

## 6. Structure et Responsabilités des Modules

| Module | Responsabilité |
|---|---|
| `src/axora/api/` | Endpoints FastAPI, conversion des requêtes HTTP en intentions agentiques |
| `src/axora/agent/` | Runtime de l'agent, boucle d'exécution, gestion du contexte et des décisions |
| `src/axora/llm/` | Interfaces et adaptateurs pour les différents fournisseurs de LLM |
| `src/axora/semantic/` | Chargement et service de consultation du modèle sémantique (YAML) |
| `src/axora/tools/` | Registre et implémentation des outils génériques (`discover_model`, `query_data`, etc.) |
| `src/axora/data/` | Connexion PostgreSQL, modèles ORM SQLAlchemy, moteur de requête dynamique |

---

**Axora — From intent to action.**
