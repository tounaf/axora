# Axora — FEAT-01 : Service Sémantique & Guide d'Installation, Démarrage et Mise en Production

**Version :** 0.5
**Statut :** Documentation technique de la fonctionnalité FEAT-01 et Guide de Déploiement/Production
**Composants :** `src/axora/semantic/` (`models.py`, `loader.py`, `service.py`, `definitions/gestion_paroissiale.yaml`)

---

## Part 1 : Spécification & Documentation Technique FEAT-01

### 1.1 Présentation de FEAT-01

FEAT-01 est le **Service de Chargement & Consultation Sémantique**. Il constitue le premier pilier d'Axora en rendant le modèle métier accessible sous forme de métadonnées structurées aux composants agentiques.

### 1.2 Architecture & Dépendances internes

```text
src/axora/semantic/
├── models.py                   # Schémas Pydantic v2 (SemanticModel, EntityDefinition, etc.)
├── loader.py                   # Fonctions de chargement et de validation du fichier YAML
├── service.py                  # Service applicatif d'inspection et de résolution sémantique
└── definitions/
    └── gestion_paroissiale.yaml # Définition YAML du domaine pilote paroissial
```

### 1.3 Utilisation dans le Code Python

```python
from axora.semantic.service import SemanticModelService

# Initialisation du service depuis le fichier YAML
service = SemanticModelService.from_yaml("src/axora/semantic/definitions/gestion_paroissiale.yaml")

# 1. Obtenir la vue d'ensemble des entités
overview = service.get_entities_overview()

# 2. Obtenir les détails d'une entité par son nom ou son synonyme (ex: 'église' -> 'Paroisse')
entity_def = service.get_entity_details("église")

# 3. Résoudre le nom canonique
canonical_name = service.resolve_concept_name("fidèle")  # Retourne 'Membre'
```

---

## Part 2 : Guide d'Installation, Démarrage et Mise en Production

### 2.1 Environnement de Développement Local (Docker Compose)

Le projet Axora s'appuie sur Docker Compose pour garantir la reproductibilité totale des environnements.

#### Procédure d'installation :

```bash
# 1. Cloner le dépôt Git
git clone <repository-url>
cd axora

# 2. Copier les variables d'environnement exemple
cp .env.example .env

# 3. Lancer la stack en arrière-plan
docker compose up --build -d

# 4. Vérifier l'état des services et des logs
docker compose ps
docker compose logs -f api
```

#### Exécution de la suite de tests unitaires :

```bash
docker compose exec api pytest
```

---

### 2.2 Guide de Déploiement & Mise en Production (Production Setup)

En environnement de production, l'application Axora doit être exécutée derrière un **Proxy Inverse / Load Balancer** (ex: Nginx, Traefik, Caddy) gérant le certificat SSL/TLS.

#### Diagramme d'Architecture de Production

```mermaid
flowchart TD
    Client[Client HTTPS Web / Mobile] --> Nginx[Nginx / Traefik Reverse Proxy HTTPS:443]

    subgraph K8s_or_Docker_Swarm["Cluster / Container Engine"]
        Nginx -- HTTP Pass --> API1[Axora API Instance 1]
        Nginx -- HTTP Pass --> API2[Axora API Instance 2]

        API1 -- Connection Pool --> PGBouncer[PgBouncer Connection Pooler]
        API2 -- Connection Pool --> PGBouncer

        PGBouncer --> Postgres[(PostgreSQL 17 Primary)]
    end
```

#### 1. Configuration des Variables d'Environnement de Production

| Variable | Description | Exemple Prod |
|---|---|---|
| `ENVIRONMENT` | Environnement d'exécution | `production` |
| `DATABASE_URL` | DSN de connexion PostgreSQL sécurisé | `postgresql+psycopg://user:strongpass@pg-cluster:5432/axora_prod` |
| `LLM_PROVIDER` | Adaptateur LLM sélectionné | `openai` ou `anthropic` |
| `LLM_API_KEY` | Clé d'API du fournisseur LLM | `sk-prod-xxxx...` |
| `MAX_AGENT_ITERATIONS` | Nombre maximal d'itérations de la boucle | `8` |

#### 2. Exemple de Dockerfile Multi-Stage de Production (`Dockerfile.prod`)

```dockerfile
# Build Stage
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final Runtime Stage
FROM python:3.12-slim AS runner

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

RUN groupadd --system app && useradd --system --gid app app

COPY --from=builder /install /usr/local
COPY src/ ./src/

USER app
EXPOSE 8000

CMD ["uvicorn", "axora.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 3. Sécurisation & Recommandations de Production

1. **Utilisateur non-root :** L'image Docker s'exécute sous l'utilisateur système restreint `app`.
2. **Gérer les pools de connexions SQL :** Employer PgBouncer ou SQLAlchemy QueuePool pour réguler le nombre de connexions ouvertes vers PostgreSQL.
3. **Healthcheck & Probes Kubernetes :**
   - Liveness Probe : `GET /health` (Port 8000, Interval 10s).
   - Readiness Probe : Vérification de la connectivité PostgreSQL via `GET /health`.

---

**Axora — From intent to action.**
