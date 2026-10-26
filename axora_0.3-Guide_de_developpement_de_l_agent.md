# Axora — Guide de développement de l'agent orienté métier

**Version :** 0.3
**Statut :** Plan d'implémentation technique et guide de développement
**Périmètre :** Conception et implémentation du cœur agentique d'Axora
**Langage :** Python 3.12 (FastAPI, Pydantic, SQLAlchemy)
**Base de données :** PostgreSQL

---

## 1. Vision et principes directeurs

L'objectif de l'agent Axora est de convertir une **intention exprimée en langage naturel** en **actions déterministes et sécurisées** sur les données métier, sans développer de code spécifique par cas d'usage.

### Principes d'ingénierie :

1. **Orchestration hybride :** Le LLM raisonne et propose des décisions structurées ; le runtime Python contrôle la boucle, valide les contrats, et exécute les outils.
2. **Découverte sémantique progressive :** L'agent découvre le modèle métier via des outils de métadonnées plutôt que de deviner la structure de la base SQL.
3. **Sécurité et requêtes paramétrées :** Le LLM ne génère **jamais** de requêtes SQL brutes. Il produit une structure d'opération abstraite que le moteur de requête traduit de manière sécurisée via SQLAlchemy.
4. **Validation déterministe par Pydantic :** Toutes les décisions du LLM et les arguments des outils sont strictement validés avant toute exécution.
5. **Indépendance du fournisseur LLM :** Le modèle de langage est masqué derrière une interface d'adaptateur interchangeable (OpenAI, Anthropic, Ollama, Gemini, etc.).

---

## 2. Architecture modulaire

La structure du code dans `src/axora/` s'organise selon les responsabilités suivantes :

```text
src/axora/
├── main.py                     # Point d'entrée FastAPI
├── config.py                   # Configuration centralisée (Pydantic Settings)
├── api/
│   └── routes.py               # Enpoints HTTP / API conversationnelle
├── agent/
│   ├── runtime.py              # Orchestrateur principal de l'agent
│   ├── loop.py                 # Boucle d'exécution bornée
│   ├── context.py              # Constructeur de contexte pour le LLM
│   └── decisions.py            # Modèles Pydantic des décisions de l'agent
├── llm/
│   ├── interface.py            # Protocol/Interface d'adaptateur LLM
│   └── provider.py             # Implémentations d'adaptateurs (e.g. OpenAI/Ollama)
├── semantic/
│   ├── service.py              # Service du modèle sémantique
│   └── loader.py               # Chargeur des définitions YAML sémantiques
├── tools/
│   ├── interface.py            # Protocole des outils génériques
│   ├── registry.py             # Registre des outils
│   ├── discover_model.py       # Outil de découverte du modèle sémantique
│   └── query_data.py          # Outil de consultation générique
└── data/
    ├── database.py             # Connexion et session SQLAlchemy
    ├── models.py               # Modèles ORM SQLAlchemy
    └── query_engine.py         # Traducteur d'opérations sémantiques en SQL
```

---

## 3. Feuille de route de développement (Roadmap par phases)

### Phase 1 : Socle technique et Configuration (Jalon 1)

**Objectif :** Valider l'infrastructure minimale et la connexion à PostgreSQL.

1. **Configuration (`src/axora/config.py`) :**
   - Utiliser `pydantic-settings` pour charger la configuration (`DATABASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `MAX_AGENT_ITERATIONS`).
2. **Base de données (`src/axora/data/database.py` & `models.py`) :**
   - Configurer le moteur asynchrone SQLAlchemy (`asyncpg` ou `psycopg3`).
   - Déclarer les modèles ORM (`Paroisse`, `ZoneGeographique`, `Membre`, `Association`, `AdhesionAssociation`, `DemandePassage`, `HistoriqueRattachement`).
3. **Tests d'intégration de la base :**
   - Écrire un test Pytest insérant et relisant un jeu de données de test (Paroisse d'Andranovelona et zone d'Andoharanofotsy).

---

### Phase 2 : Service sémantique (Jalon 2)

**Objectif :** Charger le fichier YAML du modèle sémantique et exposer les méthodes d'exploration.

1. **Chargeur (`src/axora/semantic/loader.py`) :**
   - Charger `gestion_paroissiale.yaml` et instancier des structures Pydantic fortes pour les entités, attributs, relations et règles métier.
2. **Service sémantique (`src/axora/semantic/service.py`) :**
   - `get_entities_overview()` : Retourne la liste des entités avec descriptions.
   - `get_entity_details(entity_name)` : Retourne les attributs, relations et règles d'une entité.
   - `resolve_path(start_entity, target_path)` : Résout un chemin sémantique (ex: `Membre.paroisse.nom` -> jointure `membre` -> `paroisse`).

---

### Phase 3 : Contrat de décision et Adaptateur LLM (Jalon 3)

**Objectif :** Normaliser les échanges entre le LLM et l'application.

1. **Modèle de décision (`src/axora/agent/decisions.py`) :**
   ```python
   from typing import Any, Literal
   from pydantic import BaseModel, Field, model_validator

   class ToolCall(BaseModel):
       name: str
       arguments: dict[str, Any] = Field(default_factory=dict)

   class AgentDecision(BaseModel):
       type: Literal["call_tool", "ask_user", "final_answer"]
       tool_call: ToolCall | None = None
       content: str | None = None

       @model_validator(mode="after")
       def validate_decision_structure(self):
           if self.type == "call_tool" and not self.tool_call:
               raise ValueError("Un type 'call_tool' requiert le champ 'tool_call'.")
           if self.type in ("ask_user", "final_answer") and not self.content:
               raise ValueError(f"Le type '{self.type}' requiert le champ 'content'.")
           return self
   ```

2. **Interface LLM (`src/axora/llm/interface.py`) :**
   - Définir le protocole `LLMAdapter` avec la méthode `async def decide(self, prompt: str, tools_schema: list[dict]) -> AgentDecision`.

---

### Phase 4 : Registre et Outils Génériques (Jalon 4)

**Objectif :** Implémenter les capacités `discover_model` et `query_data`.

1. **Interface et Registre (`src/axora/tools/`) :**
   - `ToolInterface` : `name`, `description`, `args_schema`, `execute(arguments)`.
   - `ToolRegistry` : Enregistrement et résolution dynamique d'outils.
2. **Outil `discover_model` :**
   - Permet à l'agent de consulter le `SemanticModelService` pour obtenir des informations sur le domaine.
3. **Moteur de Requête et Outil `query_data` (`src/axora/data/query_engine.py`) :**
   - Accepte une requête structurée :
     ```json
     {
       "entity": "Membre",
       "select": ["id", "nom", "prenom"],
       "filters": [
         {"path": "paroisse.nom", "operator": "equals", "value": "Andranovelona"},
         {"path": "zone.nom", "operator": "equals", "value": "Andoharanofotsy"}
       ],
       "limit": 50
     }
     ```
   - Traduit dynamiquement et de façon sécurisée cette structure en requête SQLAlchemy avec requêtes paramétrées.

---

### Phase 5 : Boucle d'exécution et Runtime Agent (Jalon 5)

**Objectif :** Assembler le cycle d'exécution borné en Python.

1. **Constructeur de contexte (`src/axora/agent/context.py`) :**
   - Formate le prompt système, inclut les explications du modèle sémantique déjà découvertes, l'historique des échanges et les résultats des outils précédents (observations).
2. **Boucle d'exécution (`src/axora/agent/loop.py`) :**
   ```python
   async def run_agent_loop(
       user_message: str,
       history: list[dict],
       runtime_services: RuntimeServices,
       max_iterations: int = 8
   ) -> str:
       context = build_initial_context(user_message, history)

       for iteration in range(max_iterations):
           decision = await runtime_services.llm.decide(
               context=context,
               tools=runtime_services.tools.list_schemas()
           )

           if decision.type == "final_answer":
               return decision.content

           if decision.type == "ask_user":
               return decision.content

           if decision.type == "call_tool":
               tool = runtime_services.tools.get(decision.tool_call.name)
               result = await tool.execute(decision.tool_call.arguments)
               context.append_observation(decision.tool_call, result)

       return "La demande n'a pas pu être traitée dans le nombre d'étapes imparti."
   ```

---

### Phase 6 : API FastAPI et Scenario E2E (Jalon 6)

**Objectif :** Exposer l'agent via un endpoint HTTP et valider le scénario pilote.

1. **Endpoint REST (`src/axora/api/routes.py`) :**
   - `POST /api/v1/chat` : Accepte `{ "message": "...", "conversation_id": "..." }` et retourne la réponse de l'agent.
2. **Test End-to-End (`tests/test_intent_scenarios.py`) :**
   - Scénario de test :
     > "Qui sont les membres de la paroisse Andranovelona qui habitent dans la zone d'Andoharanofotsy ?"
   - Vérifier que l'agent effectue la découverte sémantique, exécute `query_data` avec les bons filtres, et retourne la liste exacte des membres de la base de données.

---

## 4. Stratégie de Sécurité et de Robustesse

- **Contrôle d'accès aux données :** L'agent n'a pas accès à la console ni au driver SQL direct. Il interagit exclusivement par le contrat JSON de `query_data`.
- **Limites d'itération :** Un compteur strict (`max_iterations = 8`) empêche les boucles infinies ou la surconsommation de tokens.
- **Gestion des erreurs d'outils :** Si un outil renvoie une erreur (arguments invalides, entité inconnue), l'erreur est réinjectée comme observation afin que le LLM puisse corriger sa demande au tour suivant.

---

## 5. Prochaines étapes immédiates

1. **Phase 1 :** Créer la structure des répertoires `src/axora/agent/`, `src/axora/semantic/`, `src/axora/tools/`, `src/axora/llm/`.
2. **Phase 2 :** Implémenter le fichier YAML du modèle sémantique et son service de chargement.
3. **Phase 3 :** Développer le moteur `query_data` générique basé sur SQLAlchemy.
4. **Phase 4 :** Connecter la boucle agentique et valider avec le jeu de données de test.

---

**Axora — De l'intention à l'action.**
