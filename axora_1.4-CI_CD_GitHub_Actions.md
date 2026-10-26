# Axora — Workflow CI/CD GitHub Actions

**Version :** 1.4
**Statut :** Documentation technique du pipeline d intégration continue (CI)
**Fichier de configuration :** `.github/workflows/ci.yml`

---

## 1. Présentation du Workflow CI

Le workflow GitHub Actions `.github/workflows/ci.yml` automatise la validation de la qualité du code et l exécution de la suite de tests unitaires et fonctionnels à chaque `push` ou `pull_request` sur le dépôt.

---

## 2. Déroulement des Étapes du Pipeline

```mermaid
flowchart TD
    Trigger([Push / Pull Request]) --> Checkout[Checkout du Code Source]
    Checkout --> SetupPython[Installation de Python 3.12]
    SetupPython --> StartPostgreSQL[Démarrage du Service PostgreSQL 17 Container]
    StartPostgreSQL --> InstallDeps[Installation des Dépendances pip]
    InstallDeps --> RunPytest[Exécution de Pytest PYTHONPATH=src]
    RunPytest --> Result{Résultat des 40 Tests ?}
    Result -- 100% Succès --> BuildPass([CI Check PASSED])
    Result -- Échec --> BuildFail([CI Check FAILED])
```

---

## 3. Services Conteneurisés dans le Pipeline

Le workflow instancie automatiquement une base de données PostgreSQL 17 avec le healthcheck officiel `pg_isready` :

```yaml
services:
  postgres:
    image: postgres:17-alpine
    env:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: axora
    ports:
      - 5432:5432
```

---

## 4. Variables d Environnement Définies dans le CI

- `DATABASE_URL`: `postgresql+psycopg://postgres:postgres@localhost:5432/axora`
- `LLM_PROVIDER`: `mock`
- `MAX_AGENT_ITERATIONS`: `8`

---

## 5. Déclenchement Manuel et Automatique

Le pipeline est configuré pour se déclencher automatiquement sur :
- Les branches `main` et `master`.
- Toutes les branches de fonctionnalités (`jules-*`).
- Toutes les demandes de tirage (Pull Requests).

---

**Axora — From intent to action.**
