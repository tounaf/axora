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

Définir `POSTGRES_PASSWORD` avec un secret aléatoire URL-safe avant le démarrage. Exemple :

```bash
openssl rand -hex 32
```

Copier la valeur produite dans `POSTGRES_PASSWORD` dans `.env`. Ne pas réutiliser cette valeur dans un dépôt ou un ticket.

Autres paramètres :
- Le profil par défaut utilise `LLM_PROVIDER=mock` et ne nécessite aucune clé. Pour activer un fournisseur distant, configurer uniquement sa clé dans `.env`.
- Les profils optionnels `admin` (pgAdmin) et `mysql` exigent leurs propres identifiants ; ils ne sont pas démarrés par défaut.

### 3. Démarrer l'application avec Docker Compose

Lancer les containers en arrière-plan :

```bash
docker compose up --build -d
```

Cette commande démarre deux services :
- `db` : Base de données PostgreSQL 17
- `api` : Application FastAPI / Runtime Agent Axora sur le port `8000`

Le démarrage échoue explicitement si `POSTGRES_PASSWORD` n'est pas défini. Le mot de passe est généré localement et n'est pas fourni par le dépôt.

### 4. Vérifier l'état des services

- **Liveness API :** [http://localhost:8000/health](http://localhost:8000/health)
- **Readiness API + PostgreSQL :** [http://localhost:8000/health/ready](http://localhost:8000/health/ready)
- **Documentation API Swagger :** [http://localhost:8000/docs](http://localhost:8000/docs)

Le profil pgAdmin n'est pas exposé par défaut. Après avoir renseigné `PGADMIN_DEFAULT_EMAIL` et `PGADMIN_DEFAULT_PASSWORD` dans `.env`, le démarrer explicitement :

```bash
docker compose --profile admin up -d pgadmin
```

Le profil MySQL est réservé aux environnements qui ont renseigné `MYSQL_ROOT_PASSWORD` et `MYSQL_PASSWORD` :

```bash
docker compose --profile mysql up -d mysql
```

---

## 🧪 Exécution des Tests

Les tests automatiques s'exécutent directement dans le container de l'application :

```bash
docker compose exec api pytest
```

## Importer un dump SQL dans MySQL (prototype)

Le parcours prototype `install-mysql` suppose que Docker, son daemon et le plugin Compose sont déjà installés et accessibles. Il réutilise le service `mysql` existant de `compose.yaml`, construit et démarre l'API depuis le `Dockerfile` du dépôt avec le manifeste généré, importe le dump SQL fourni, puis génère le manifeste sémantique à partir du schéma détecté.

Commencer par valider le plan sans créer de ressources :

```bash
PYTHONPATH=src python -m axora.cli install-mysql \
  --sql-file /chemin/vers/mon_dump.sql \
  --output ./manifest_test.yaml \
  --plan
```

Après vérification, lancer le parcours interactif :

```bash
PYTHONPATH=src python -m axora.cli install-mysql \
  --sql-file /chemin/vers/mon_dump.sql \
  --output ./manifest_test.yaml
```

L'installation demande confirmation avant de démarrer Compose et d'exécuter le SQL. Les ports publiés par défaut sont `127.0.0.1:3307` pour MySQL et `127.0.0.1:8001` pour l'API ; si l'un est déjà utilisé, choisissez un autre avec `--port` ou `--api-port`. Le healthcheck MySQL vérifie le serveur final sur TCP, et non le socket temporaire utilisé pendant l'initialisation. Axora réutilise le projet Compose `axora` et son volume persistant `axora_axora-mysql-data` lors des lancements suivants ; le même dump n'est pas réimporté. Une base déjà présente mais non enregistrée par Axora n'est jamais écrasée. Le manifeste est créé sous `src/axora/semantic/definitions/` par défaut, et l'état/les secrets de connexion sont enregistrés dans `~/.config/axora/installations/` avec des permissions privées. Ne partagez pas ces fichiers.

Un dump qui contient `USE` ou `CREATE DATABASE` doit cibler une seule base ; son nom est détecté automatiquement, ou doit correspondre à `--database`. `--database`, `--name`, `--output`, `--port` et `--api-port` permettent de personnaliser ces valeurs. Si le manifeste existe déjà, choisissez un autre `--output` ou confirmez son remplacement avec `--overwrite`. `--yes` supprime la confirmation interactive et ne doit être utilisé que si le plan est accepté.

Cette première tranche n'installe pas Docker ni ne configure de fournisseur LLM. Sans clé LLM fournie par l'utilisateur, l'application reste en mode démo. L'import exécute le fichier SQL comme `root` dans le service MySQL du Compose Axora : n'utilisez que des dumps de confiance. Les conteneurs et volumes ne sont jamais supprimés automatiquement.

---

## 📁 Architecture et Structure du Projet

```text
axora/
├── compose.yaml                # Déploiement courant Docker Compose (API + PostgreSQL)
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
- [Architecture des Connecteurs BDD Pluggables v3.0](axora_3.0-Architecture_Connecteurs_BDD_Pluggables_Extensions.md)
- [Jalon 1 : Conception & Implémentation Connecteurs Core (Postgres & SQLite) v3.1](axora_3.1-Jalon_1_Conception_et_Implementation_Connecteurs_BDD_Core_Postgres_SQLite.md)
- [Jalon 2 : Conception & Implémentation Connecteur MySQL & MariaDB v3.2](axora_3.2-Jalon_2_Conception_et_Implementation_Connecteur_MySQL_MariaDB.md)
- [Jalon 6 : Auto-Introspection & Reverse-Engineering v3.6](axora_3.6-Jalon_6_Auto-Introspection_Reverse-Engineering.md)
- [Jalon 7 : Installation Autonome et Préparation de l'Environnement v3.7](axora_3.7-Jalon_7_Installation_Autonome_Axora.md)

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
