# AXORA - Jalon 6 : Auto-Introspection & Reverse-Engineering

> **Document de Specification Technique & Etat d'Implementation (v3.6)**  
> *Generation automatique d'un manifeste semantique Axora depuis une base SQL live ou un fichier DDL.*

---

## 1. Objectif

Le Jalon 6 vise la commande suivante :

```bash
PYTHONPATH=src python3 -m axora.cli introspect --db-url "mysql://..." --output modele_auto.yaml
```

Il doit extraire automatiquement les tables, colonnes, clefs primaires, clefs etrangeres et relations, puis produire un manifeste semantique compatible avec le modele Axora.

---

## 2. Architecture Implementee

```text
src/axora/extensions/bdd/introspector/
├── interface.py
├── db_introspector.py
├── sql_dump_parser.py
├── schema_reverse_engine.py
└── __init__.py
```

La chaïne est composee de :

1. `LiveDatabaseIntrospector` pour une base SQLAlchemy live ;
2. `SQLDumpParser` pour un dump ou fichier DDL ;
3. `SchemaReverseEngine` pour transformer le schema technique en modele semantique ;
4. la sous-commande CLI `introspect`.

---

## 3. Fonctionnalites Disponibles

### Base live

La commande accepte `--db-url` et utilise SQLAlchemy Inspector.

URL synchrones prises en charge :

- PostgreSQL : `postgresql://` et `postgresql+psycopg://`
- SQLite : `sqlite://` et `sqlite+aiosqlite://`
- MySQL/MariaDB : `mysql://`, `mariadb://`, `mysql+aiomysql://`, `mysql+asyncmy://`

Les URL async sont transpotees vers un pilote synchrone pour SQLAlchemy Inspector.

### Fichier `.sql`

La commande accepte `--sql-file` pour parser un dump ou un fichier DDL SQL. La source `--sql-file` et la source `--db-url` sont mutuellement exclusives.

Elle extrait notamment :

- CREATE TABLE ;
- clefs primaires inline, table-level et declarees par `ALTER TABLE` ;
- clefs etrangeres inline, table-level et declarees par `ALTER TABLE` ;
- colonnes et types SQL ;
- tables de jonction ;
- relations many-to-many.

Le parseur gere les identifiants entre backticks, guillemets doubles ou crochets, les definitions sur plusieurs lignes, les types parametres (ex. `VARCHAR(120)`), les contraintes composees et les virgules imbriquees dans les declarations.

Exemple de fichier source :

```sql
CREATE TABLE parish (
  id INTEGER PRIMARY KEY,
  name VARCHAR(120) NOT NULL
);

CREATE TABLE member (
  id INTEGER PRIMARY KEY,
  parish_id INTEGER,
  CONSTRAINT fk_member_parish FOREIGN KEY (parish_id) REFERENCES parish(id)
);
```

### Export

Les options suivantes sont disponibles :

- `--output <chemin>` : fichier YAML de sortie ;
- `--name <nom>` : nom du modele semantique.

---

## 4. Reverse-Engineering

`SchemaReverseEngine` genere :

- une entite par table metier ;
- le nom de table dans `storage.table` ;
- la clef primaire dans `storage.id` ;
- les attributs et types semantiques ;
- les relations many-to-one ;
- les relations inverses one-to-many ;
- les relations many-to-many via les tables de jonction ;
- des synonymes techniques ;
- une regle d'integrite referentielle par defaut.

Les tables techniques comme `messenger_messages`, `doctrine_migration_versions` et `alembic_version` sont exclues.

---

## 5. Utilisation

### Dump SQL

```bash
PYTHONPATH=src python3 -m axora.cli introspect \
  --sql-file fvavitao_identity.sql \
  --output src/axora/semantic/definitions/identite_auto.yaml
```

Le nom du modele est derive du nom du fichier, sauf si `--name` est fourni. Sans `--output`, le manifeste est ecrit dans `src/axora/semantic/definitions/<nom>.yaml`.

### Base live

```bash
PYTHONPATH=src python3 -m axora.cli introspect \
  --db-url "mysql://localhost:3306/axora" \
  --output src/axora/semantic/definitions/mysql_auto.yaml
```

---

## 6. Validation

```bash
PYTHONPATH=src python3 -m pytest tests/test_introspector.py
```

Resultat actuel : **11 tests passent**, couvrant le parsing du dump fourni, les contraintes inline et composites, les contraintes `ALTER TABLE`, l'export YAML, la normalisation des URL, le parcours CLI et le chargement du manifeste genere par le validateur semantique Axora.

Smoke test CLI :

```bash
PYTHONPATH=src python3 -m axora.cli introspect \
  --sql-file fvavitao_identity.sql \
  --output /tmp/jalon6-audit.yaml
```

Le fichier genere contient les entites detectees et est utilisable comme manifeste YAML.

---

## 7. Etat d'Implementation

| Exigence | Etat |
|---|---|
| Sous-commande CLI `introspect` | Implémentée |
| Source SQL live | Implémentée via SQLAlchemy Inspector |
| Source fichier SQL | Implémentée |
| Extraction tables/colonnes | Implémentée |
| Extraction clefs primaires | Implémentée |
| Extraction clefs etrangeres | Implémentée |
| Generation des relations | Implémentée |
| Detection des tables de jonction | Implémentée |
| Export YAML | Implémentée |
| Documentation du jalon | Implémentée |

---

## 8. Ecarts Restants

- Les pilotes synchrone live PostgreSQL/MySQL sont resolus, mais les tests live necessitent une base réellement accessible.
- Le nom exact recommande par la feuille de route, `inspect-db`, n'est pas utilise : la CLI dispose de `introspect`, avec des options plus explicites.
- L'introspection live ne couvre pas MongoDB, MS SQL Server et Oracle.
- Le parser SQL reste principalement optimise pour les syntaxes CREATE TABLE MySQL/PostgreSQL.
- Les descriptions métier, les allowed_values complexes et les règles métier spécifiques nécessitent une revue humaine du YAML genere.
