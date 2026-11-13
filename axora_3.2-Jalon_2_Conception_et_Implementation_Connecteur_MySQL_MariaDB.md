# AXORA — Conception & Implémentation du Jalon 2 : Connecteur MySQL & MariaDB

> **Document de Spécification Technique & Guide d'Implémentation (v3.2)**  
> *Mise en œuvre du Jalon 2 de l'architecture pluggable : pilote MySQL/MariaDB asynchrone, transposition des UUID, gestion du pooling et encodage utf8mb4.*

---

## 🎯 1. Contexte & Objectifs du Jalon 2

Dans la continuité de la feuille de route **Axora v3.0** ([axora_3.0-Architecture_Connecteurs_BDD_Pluggables_Extensions.md](file:///home/fetraharinjatovo/Architecture%20Plateform/axora/axora_3.0-Architecture_Connecteurs_BDD_Pluggables_Extensions.md)) et du socle d'abstraction fondé au **Jalon 1** ([axora_3.1-Jalon_1_Conception_et_Implementation_Connecteurs_BDD_Core_Postgres_SQLite.md](file:///home/fetraharinjatovo/Architecture%20Plateform/axora/axora_3.1-Jalon_1_Conception_et_Implementation_Connecteurs_BDD_Core_Postgres_SQLite.md)), le **Jalon 2** intègre le support complet des bases de données relationnelles **MySQL** (version 8.0+) et **MariaDB** (version 10.5+).

### Défis techniques adressés par le Jalon 2 :
1. **Pilote Asynchrone Python** : Intégration de `aiomysql` (conforme PEP 249 asyncio) et support alternatif de `asyncmy`.
2. **Absence de Type UUID Natif** : Contrairement à PostgreSQL, MySQL ne possède pas de type `UUID` standardisé. Axora transpose dynamiquement les identifiants en `CHAR(36)`.
3. **Erreur « MySQL server has gone away »** : Configuration automatique du recyclage de connexions (`pool_recycle=3600`) et sonde active avant exécution (`pool_pre_ping=True`).
4. **Encodage Multilingue & Emojis** : Injection automatique du paramètre `charset=utf8mb4` dans les chaînes de connexion.
5. **Gestion des Identifiants Réservés** : Utilisation automatique des backticks `` `table` `` et `` `colonne` `` via la compilation du dialecte SQLAlchemy MySQL.
6. **Support Dockerisé** : Ajout d'un service MySQL 8.4 dans [compose.yaml](file:///home/fetraharinjatovo/Architecture%20Plateform/axora/compose.yaml) sous profil dédié.

---

## 📐 2. Conception Architecturelle & Diagrammes

### 2.1 Diagramme de Classes (Extension du Socle Jalon 1)

```mermaid
classDiagram
    class DatabaseConnectorInterface {
        <<interface>>
        +dialect_name: str
        +is_nosql: bool
        +connect() None
        +disconnect() None
        +health_check() dict
        +execute_query(entity_def, select_fields, filters, limit) list
        +execute_mutation(entity_def, action, payload, record_id) dict
    }

    class SQLBaseConnector {
        -raw_url: str
        -semantic_service: SemanticModelService
        #_engine: AsyncEngine
        #_session_factory: async_sessionmaker
        +connect() None
        +disconnect() None
        +health_check() dict
        +execute_query() list
        +execute_mutation() dict
    }

    class PostgresConnector {
        +dialect_name = "postgresql"
        #_normalize_url(url) str
    }

    class SqliteConnector {
        +dialect_name = "sqlite"
        #_normalize_url(url) str
    }

    class MySQLConnector {
        +dialect_name = "mysql"
        #_normalize_url(url) str
        +connect() None
    }

    class ConnectorRegistry {
        +register(scheme, connector_cls) None
        +get(scheme) Type
        +create(url, semantic_service) DatabaseConnectorInterface
    }

    DatabaseConnectorInterface <|-- SQLBaseConnector
    SQLBaseConnector <|-- PostgresConnector
    SQLBaseConnector <|-- SqliteConnector
    SQLBaseConnector <|-- MySQLConnector
    ConnectorRegistry ..> MySQLConnector : instancie
```

### 2.2 Séquence de Résolution & Normalisation d'URI MySQL

```mermaid
sequenceDiagram
    autonumber
    participant App as Application / Tool
    participant Factory as get_connector()
    participant Registry as ConnectorRegistry
    participant MySQL as MySQLConnector
    participant Dialect as SQLAlchemy Engine (mysql+aiomysql)

    App->>Factory: get_connector("mysql://axora:pwd@localhost:3306/axora")
    Factory->>Registry: create(url)
    Registry->>Registry: Extrait le scheme "mysql" -> MySQLConnector
    Registry->>MySQL: __init__(url, pool_pre_ping=True, pool_recycle=3600)
    MySQL->>MySQL: _normalize_url("mysql://...")
    Note over MySQL: 1. Réécriture : mysql+aiomysql://<br/>2. Paramètres : charset=utf8mb4
    MySQL->>Dialect: create_async_engine(normalized_url)
    MySQL-->>App: Instance MySQLConnector prête
```

---

## ⚙️ 3. Spécifications Techniques et Particularités

### 3.1 Transposition Automatique des Types GUID
Dans [src/axora/data/dynamic_models.py](file:///home/fetraharinjatovo/Architecture%20Plateform/axora/src/axora/data/dynamic_models.py), le type `GUID` hérite de `TypeDecorator` et détecte dynamiquement le dialecte cible :

```python
class GUID(TypeDecorator):
    impl = CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            # Pour MySQL, MariaDB, SQLite : stockage textuel normalisé
            return dialect.type_descriptor(CHAR(36))
```

Cette abstraction garantit que les clés primaires et étrangères générées à partir du manifeste sémantique sont représentées sous forme de colonnes `CHAR(36)` optimisées sous MySQL, tout en restant transparentes pour l'Agent.

### 3.2 Gestion du Cycle de Vie et Robustesse du Pool
Par défaut, MySQL ferme brutalement les connexions inactives après 8 heures (`wait_timeout`). `MySQLConnector` applique par défaut :
- `pool_recycle = 3600` (1 heure) : renouvelle proactivement les connexions inactives.
- `pool_pre_ping = True` : teste la vivacité de chaque connexion (`SELECT 1`) avant de la confier à une session applicative.

### 3.3 Normalisation d'URI et Charset UTF8MB4
La méthode `_normalize_url` :
1. Remplace `mysql://` ou `mariadb://` par `mysql+aiomysql://`.
2. Inspecte la chaîne de requête (query string) et y injecte `charset=utf8mb4` si absent, assurant la prise en charge des caractères accentués et émojis.

---

## 📁 4. Arborescence du Code & Fichiers Modifiés

```text
src/axora/extensions/bdd/
├── __init__.py           # Enregistrement des 5 schémas MySQL/MariaDB
├── interface.py          # Contrat DatabaseConnectorInterface
├── registry.py           # Registre dynamique
└── sql/
    ├── __init__.py       # Export de MySQLConnector
    ├── base.py           # SQLBaseConnector
    ├── postgres.py       # PostgresConnector
    ├── sqlite.py         # SqliteConnector
    └── mysql.py          # [NOUVEAU] MySQLConnector

compose.yaml              # Ajout du service optionnel MySQL 8.4 (profil 'mysql')
requirements.txt          # Ajout de aiomysql et cryptography
tests/
└── test_mysql_connector.py # [NOUVEAU] Suite de tests MySQL dédiée
```

---

## 🧪 5. Stratégie de Test et Validation

La suite de tests unitaires et de compilation dialectale a été ajoutée dans **[tests/test_mysql_connector.py](file:///home/fetraharinjatovo/Architecture%20Plateform/axora/tests/test_mysql_connector.py)** :

| Nom du Test | Périmètre | Résultat Attendu |
|---|---|---|
| `test_mysql_schemes_registered` | Registre de drivers | `mysql`, `mysql+aiomysql`, `mysql+asyncmy`, `mariadb`, `mariadb+aiomysql` renvoient tous une instance `MySQLConnector`. |
| `test_mysql_url_normalization` | Réécriture d'URL | Conversion en `mysql+aiomysql://` et injection automatique de `charset=utf8mb4`. |
| `test_mysql_engine_defaults` | Robustesse du pool | Vérification de `pool_pre_ping=True` et `pool_recycle=3600`. |
| `test_mysql_safe_log_url` | Observabilité & Sécurité | Masquage des mots de passe (`admin:****@host:3306/db`). |
| `test_mysql_dialect_guid_transposition` | Types de données | Compilation du type `GUID()` en `CHAR(36)` pour le dialecte MySQL. |
| `test_mysql_query_compilation_with_backticks` | Compilation SQL | Échappement des tables et colonnes par des backticks (ex: `` `membre` ``). |

---

## 🚀 6. Guide de Démarrage Rapide avec MySQL

### 6.1 Démarrer le conteneur MySQL de développement
Le fichier [compose.yaml](file:///home/fetraharinjatovo/Architecture%20Plateform/axora/compose.yaml) contient le conteneur MySQL sous le profil `mysql` :

```bash
docker compose --profile mysql up -d mysql
```

### 6.2 Configurer `.env`
Dans votre fichier `.env` :

```env
# Connexion directe au conteneur MySQL
DATABASE_URL=mysql+aiomysql://axora:axorapassword@localhost:3306/axora
```

### 6.3 Utilisation en Python
```python
from axora.extensions.bdd import get_connector
from axora.semantic.service import SemanticModelService

semantic_service = SemanticModelService.from_yaml("src/axora/semantic/definitions/gestion_paroissiale.yaml")

# Instanciation automatique du connecteur MySQL
connector = get_connector(
    "mysql://axora:axorapassword@localhost:3306/axora",
    semantic_service=semantic_service,
)

# Initialisation des tables à partir du manifeste sémantique
await connector.init_schema()

# Vérification de santé
health = await connector.health_check()
print(f"Statut : {health['status']} | Dialecte : {health['dialect']} | Latence : {health['latency_ms']}ms")
```

---

## 🏁 Bilan du Jalon 2

- [x] Pilote `MySQLConnector` implémenté dans [src/axora/extensions/bdd/sql/mysql.py](file:///home/fetraharinjatovo/Architecture%20Plateform/axora/src/axora/extensions/bdd/sql/mysql.py).
- [x] Enregistrement multi-schémas (`mysql`, `mariadb`, etc.) dans [src/axora/extensions/bdd/__init__.py](file:///home/fetraharinjatovo/Architecture%20Plateform/axora/src/axora/extensions/bdd/__init__.py).
- [x] Transposition des GUID en `CHAR(36)` et compilation avec backticks validée.
- [x] Gestion de `pool_recycle` et encodage `utf8mb4`.
- [x] Service Docker Compose MySQL 8.4 configuré dans [compose.yaml](file:///home/fetraharinjatovo/Architecture%20Plateform/axora/compose.yaml).
- [x] Suite de tests [tests/test_mysql_connector.py](file:///home/fetraharinjatovo/Architecture%20Plateform/axora/tests/test_mysql_connector.py) créée.
- [x] Prochaine étape : **Jalon 3** (Connecteur MongoDB - Premier Moteur NoSQL & Pipeline d'Agrégation).
