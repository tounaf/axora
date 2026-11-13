# AXORA — Architecture des Connecteurs de Base de Données Pluggables & Extensibles

> **Document de Conception Architecturelle & Feuille de Route d'Implémentation (v3.0)**
> *Généralisation d'Axora vers une plateforme multi-bases : PostgreSQL, MySQL/MariaDB, SQLite, MongoDB (NoSQL), MS SQL Server et Oracle.*

---

## 🎯 1. Vision et Objectifs Stratégiques

### 1.1 Le Défi de la Généralisation
Jusqu'au MVP, Axora était principalement branché sur **PostgreSQL** (avec fallback en mémoire **SQLite** pour les tests automatiques).
Pour devenir une plateforme de données universelle pilotée par l'intention, Axora doit pouvoir se connecter à **n'importe quelle source de données d'entreprise** sans modifier le code de l'agent, des outils ou des modèles sémantiques.

### 1.2 Principes Directeurs
1. **Isolation Complète par Extension** : Tout connecteur de données résidera dans un dossier dédié `src/axora/extensions/bdd/` (ou `connectors/`).
2. **Design Pattern Registry & Factory (SPI - Service Provider Interface)** :
   - Auto-découverte des connecteurs selon le schéma d'URI (ex: `postgresql://`, `mysql://`, `mongodb://`, `mssql://`, `oracle://`).
   - Injection à chaud sans recompilation ni modification du cœur.
3. **Double Moteur SQL & NoSQL Unifié** :
   - Pour les bases relationnelles SQL : Traduction via SQLAlchemy Async / Dialectes optimisés.
   - Pour les bases documentaires NoSQL (MongoDB) : Moteur de requête sur pipeline d'agrégation MQL (MongoDB Query Language).
4. **Indépendance Vis-à-Vis du Schéma** : L'Agent utilise uniquement le `SemanticModelService` abstrait. Le connecteur se charge de la transposition technique vers les tables ou les collections.

---

## 📁 2. Arborescence Cible dans `src/axora/extensions/bdd/`

```text
src/axora/extensions/bdd/
├── __init__.py                  # Point d'entrée et factory globale `get_connector(url)`
├── interface.py                 # Contrats abstraits (ConnectorInterface, QueryExecutor, Introspector)
├── registry.py                  # Registre d'enregistrement dynamique des drivers
│
├── sql/                         # Famille 1 : Bases de Données Relationnelles (SQL)
│   ├── base.py                  # Connecteur SQL générique (Session management, engine pooling)
│   ├── postgres.py              # Driver PostgreSQL (psycopg3 / asyncpg, UUID natif, JSONB)
│   ├── mysql.py                 # Driver MySQL / MariaDB (aiomysql, backticks, collation)
│   ├── sqlite.py                # Driver SQLite local / embarqué (aiosqlite)
│   ├── mssql.py                 # Driver Microsoft SQL Server (aioodbc, T-SQL, TOP vs LIMIT)
│   └── oracle.py                # Driver Oracle DB (oracledb async, pagination FETCH FIRST)
│
├── nosql/                       # Famille 2 : Bases Documentaires & NoSQL
│   ├── base.py                  # Connecteur NoSQL abstrait (Collections, documents, ObjectId)
│   └── mongodb.py               # Driver MongoDB (Motor async driver, mapping pipeline $match, $lookup)
│
└── introspector/                # Moteur d'Auto-Découverte & Reverse Engineering
    ├── interface.py             # Interface d'extraction de schéma
    └── schema_reverse_engine.py # Génère automatiquement un `semantic.yaml` depuis une BDD existante !
```

---

## 📐 3. Contrats et Interfaces Techniques

### 3.1 Contrat Fondamental : `DatabaseConnectorInterface`
Chaque connecteur implémente un cycle de vie standardisé :

```python
from abc import ABC, abstractmethod
from typing import Any
from axora.semantic.models import EntityDefinition

class DatabaseConnectorInterface(ABC):
    """Contrat universel de connexion à une source de données."""

    @property
    @abstractmethod
    def dialect_name(self) -> str:
        """Nom du dialecte (ex: 'postgresql', 'mysql', 'mongodb', 'oracle', 'mssql', 'sqlite')."""
        pass

    @property
    @abstractmethod
    def is_nosql(self) -> bool:
        """Indique si le connecteur est de type documentaire/NoSQL."""
        pass

    @abstractmethod
    async def connect(self) -> None:
        """Initialise le pool de connexions asynchrone."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Ferme proprement les connexions actives."""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Vérifie la disponibilité de la base de données (ping/latence)."""
        pass

    @abstractmethod
    async def execute_query(
        self,
        entity_def: EntityDefinition,
        select_fields: list[str] | None = None,
        filters: list[dict[str, Any]] | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Exécute une requête sémantique et retourne une liste de dictionnaires normalisés."""
        pass

    @abstractmethod
    async def execute_mutation(
        self,
        entity_def: EntityDefinition,
        action: str,  # 'create', 'update', 'delete'
        payload: dict[str, Any],
        record_id: Any | None = None,
    ) -> dict[str, Any]:
        """Exécute une création ou mise à jour de données."""
        pass
```

---

## 🔍 4. Analyse Technique par Moteur de Données

| Moteur | Pilote Asynchrone Python | Particularités & Défis Techniques | Stratégie d'Adaptation |
|---|---|---|---|
| **PostgreSQL** | `psycopg` (v3) / `asyncpg` | UUID natif, JSONB, ILIKE sensible à la casse | Moteur actuel optimisé avec schéma dynamic SQLAlchemy. |
| **MySQL / MariaDB** | `aiomysql` / `asyncmy` | Pas de type UUID natif (`CHAR(36)` ou `BINARY(16)`), backticks pour échappement des mots réservés. | Transposition automatique des UUID en CHAR(36) et paramétrage du mode ANSI_QUOTES. |
| **SQLite** | `aiosqlite` | Fichier local sans serveur, verrous en écriture | Idéal pour mode embarqué desktop/mobile sans Docker. |
| **MongoDB (NoSQL)** | `motor` (Async PyMongo) | Pas de tables ni colonnes mais des **Collections** et **Documents BSON**. Relations via `_id` ou tableaux imbriqués. | Traduction des filtres en syntaxe MQL `$match`, et des relations Many-to-Many en `$lookup` ou dénormalisation de listes. |
| **MS SQL Server** | `aioodbc` | Pagination `OFFSET ... FETCH NEXT` (pas de `LIMIT`), types NVARCHAR, schémas `dbo`. | Compilation SQLAlchemy dialecte `mssql+aioodbc`. |
| **Oracle Database** | `python-oracledb` (mode async) | Noms de colonnes souvent en majuscules par défaut, pas de LIMIT classique, séquences vs IDENTITY. | Mapping casse-insensible des attributs et dialecte `oracle+oracledb`. |

---

## 🗺️ 5. Feuille de Route d'Implémentation Étape par Étape (Roadmap)

Pour garantir une stabilité absolue et éviter toute régression sur les 77 tests existants, nous préconisons un déploiement progressif en **6 jalons (Milestones)** :

```text
Jalon 1 (Core & Refacto)     ──►  Création de `src/axora/extensions/bdd/` + Connecteurs PostgreSQL & SQLite
          │
Jalon 2 (MySQL & MariaDB)    ──►  Ajout du driver `mysql.py` (Docker test container MySQL)
          │
Jalon 3 (MongoDB NoSQL)      ──►  Ajout de `mongodb.py` avec adaptateur sémantique Document-to-Entity
          │
Jalon 4 (MS SQL Server)      ──►  Driver `mssql.py` (Support T-SQL et dialectes Windows Server)
          │
Jalon 5 (Oracle Database)    ──►  Driver `oracle.py` (Mode Thin async)
          │
Jalon 6 (Auto-Introspection) ──►  Outil CLI d'introspection automatique : `axora inspect-db <url>`
```

### Détail des Jalons :

#### 🔹 Jalon 1 : Abstraction Fondatrice & Refactoring Non-Régression
- Création du dossier `src/axora/extensions/bdd/`.
- Définition des interfaces formelles (`interface.py`, `registry.py`).
- Migration du `QueryEngine` existant vers `SQLBaseConnector` avec drivers `PostgresConnector` et `SqliteConnector`.
- Validation : Les 77 tests existants doivent passer à 100%.

#### 🔹 Jalon 2 : Connecteur MySQL & MariaDB
- Implémentation de `src/axora/extensions/bdd/sql/mysql.py`.
- Gestion des spécificités MySQL (autoincrement, types GUID en CHAR(36), dialecte `mysql+aiomysql`).
- Suite de tests dédiés sur conteneur MySQL.

#### 🔹 Jalon 3 : Connecteur MongoDB (Premier Moteur NoSQL)
- Implémentation de `src/axora/extensions/bdd/nosql/mongodb.py`.
- Résolution dynamique :
  - `storage.table` dans le YAML devient le nom de la **collection** MongoDB.
  - Les requêtes et jointures Many-to-Many s'exécutent via l'Aggregation Pipeline (`$lookup`, `$unwind`, `$match`).
- Support des filtres sémantiques universels en requêtes BSON.

#### 🔹 Jalon 4 : Connecteur Microsoft SQL Server (Azure SQL / On-Premise)
- Implémentation de `src/axora/extensions/bdd/sql/mssql.py`.
- Gestion du driver ODBC asynchrone et de la pagination T-SQL.

#### 🔹 Jalon 5 : Connecteur Oracle Database
- Implémentation de `src/axora/extensions/bdd/sql/oracle.py` avec `python-oracledb` en mode *thin* (sans nécessiter les lourds binaires Oracle Instant Client).

#### 🔹 Jalon 6 : Outil CLI d'Auto-Introspection & Reverse-Engineering
- Commande CLI : `PYTHONPATH=src python3 -m axora.cli introspect --db-url "mysql://..." --output modele_auto.yaml`.
- Génère automatiquement le manifeste sémantique Axora à partir des tables et clés étrangères existantes de n'importe quelle BDD !

---

## 💡 6. Configuration dans `.env`

L'utilisateur pourra changer de base de données simplement en changeant la chaîne de connexion :

```env
# Exemples de bascule instantanée selon l'infrastructure :
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/axora
# ou
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/axora
# ou
DATABASE_URL=mongodb://localhost:27017/axora_db
# ou
DATABASE_URL=mssql+aioodbc://sa:Password123!@localhost:1433/axora?driver=ODBC+Driver+18+for+SQL+Server
# ou
DATABASE_URL=oracle+oracledb://system:oracle@localhost:1521/XEPDB1
```

---

*Spécification d'architecture et roadmap établies pour la généralisation d'Axora v3.0.*
