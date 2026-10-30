# Axora — From intent to action.

Axora est une application de données nativement orientée IA et pilotée par l'intention métier. Elle permet aux utilisateurs d'interagir avec leurs données métier en langage naturel, sans nécessiter le développement d'API ou d'interfaces dédiées pour chaque nouveau besoin.

---

## 🚀 Démarrage Rapide (Onboarding Développeur)

Le projet Axora est entièrement containerisé avec **Docker Compose** pour garantir un environnement de développement simple, reproductible et identique pour toute l'équipe.

### Prérequis

- **Docker Engine** (v24.0+) et **Docker Compose** (v2.20+)
- **Git**
- *(Optionnel)* Python 3.12+ pour le développement hors container

---

## 🛠️ Installation et Lancement

### 1. Cloner le dépôt

```bash
git clone <repository-url>
cd axora
```

### 2. Configurer les variables d'environnement

Copier le fichier d'exemple `.env.example` vers `.env` :

```bash
cp .env.example .env
```

Ajuster si nécessaire les variables dans `.env` :
- `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`
- `LLM_API_KEY` / `LLM_MODEL` (pour les appels au fournisseur LLM)

### 3. Démarrer l'application avec Docker Compose

Lancer les containers en arrière-plan :

```bash
docker compose up --build -d
```

Cette commande démarre deux services :
- `db` : Base de données PostgreSQL 17
- `api` : Application FastAPI / Runtime Agent Axora sur le port `8000`

### 4. Vérifier l'état des services

- **Healthcheck API :** [http://localhost:8000/health](http://localhost:8000/health)
- **Documentation API Swagger :** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Exécution des Tests

Les tests automatiques s'exécutent directement dans le container de l'application :

```bash
docker compose exec api pytest
```

---

## 📁 Architecture et Structure du Projet

```text
axora/
├── compose.yaml                # Configuration Docker Compose (API + PostgreSQL)
├── Dockerfile                  # Image Docker pour l'application Python
├── .env.example                # Modèle des variables d'environnement
├── requirements.txt            # Dépendances Python du projet
├── CONTRIBUTING.md             # Guide des règles & bonnes pratiques de développement
├── README.md                   # Guide principal d'installation & onboarding
├── axora_0.2-Architecture...   # Spécification technique de l'architecture MVP
├── axora_0.2-Modele_de_...     # Spécification du modèle de données et sémantique
├── axora_0.3-Guide_de_...      # Guide d'implémentation de l'agent métier
├── src/
│   └── axora/                  # Code source principal
│       ├── main.py             # Point d'entrée de l'application FastAPI
│       ├── config.py           # Configuration centralisée Pydantic
│       ├── api/                # Enpoints REST HTTP
│       ├── agent/              # Runtime, boucle d'exécution et décisions de l'agent
│       ├── llm/                # Adaptateurs et interfaces LLM
│       ├── semantic/           # Service du modèle sémantique
│       ├── tools/              # Registre et outils génériques (discover_model, query_data)
│       └── data/               # Connexion DB, modèles ORM SQLAlchemy, moteur de requête
└── tests/                      # Tests unitaires et d'intégration (pytest)
```

---

## 📖 Documents de Référence

- [Règles de Contribution & Bonnes Pratiques](CONTRIBUTING.md)
- [Architecture Technique du MVP](axora_0.2-Architecture_technique_du_MVP.md)
- [Modèle de Données et Modèle Sémantique (v0.2)](axora_0.2-Modele_de_donnees_initial_et_modele_semantique.md)
- [Guide de Développement de l'Agent Métier (v0.3)](axora_0.3-Guide_de_developpement_de_l_agent.md)

---

**Axora — From intent to action.**


---

---

## 🌐 Interface Web Dashboard (FEAT-08)

Axora propose un **Dashboard Web 3 Colonnes** interactif (`/ui`) intégrant :
1. **Sidebar Navigation** (`Assistant`, `Modèle Métier`, `Données`, `Outils`).
2. **Zone de Chat Centrale** avec accordéons d'exécution (`discover_model`, `query_data`), tableaux interactifs et boutons d'actions rapides.
3. **Inspecteur Contextuel Droit** affichant les concepts canoniques mobilisés, les jointures SQL et les règles métier appliquées.

### Lancement du Frontend Next.js (Application Autonome)

```bash
cd web

# 1. Installation des dépendances
npm install

# 2. Configuration d'environnement
echo "NEXT_PUBLIC_AXORA_API_URL=http://localhost:8000/api/v1" > .env.local

# 3. Lancement en Mode Développement
npm run dev

# 4. Lancement en Mode Production
npm run build && npm run start
```

### URLs d'Accès

- **Dashboard Web (FastAPI App)** : [http://localhost:8000/ui](http://localhost:8000/ui)
- **Dashboard Web (Next.js App)** : [http://localhost:3000](http://localhost:3000)
- **Documentation API Swagger** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **Spécification Technique FEAT-08** : [Conception Web Dashboard](axora_2.1-FEAT-08_Conception_Interface_Web_Dashboard.md)
