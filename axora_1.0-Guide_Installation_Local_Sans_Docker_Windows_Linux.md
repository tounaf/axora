# Axora — Guide d Installation et de Lancement Local sans Docker (Windows & Linux)

**Version :** 1.0
**Statut :** Guide officiel de configuration hors container pour développeurs
**Systèmes supportés :** Windows 10/11 (PowerShell & WSL2) et Linux (Ubuntu / Debian / RHEL)

---

## 1. Prérequis Système Obligatoires

Avant de commencer l installation d Axora en local sans Docker, assurez-vous de disposer des éléments suivants :

1. **Python 3.12+**
   - Téléchargement officiel : [python.org/downloads](https://www.python.org/downloads/)
   - **Important Windows :** Cochez la case **"Add python.exe to PATH"** lors de l installation.
2. **PostgreSQL 16 ou 17**
   - Windows : Installez PostgreSQL via l installateur graphique EDB ([enterprisedb.com/downloads](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)).
   - Linux : Installez via le gestionnaire de paquets de votre distribution (`apt` ou `dnf`).
3. **Git**
   - [git-scm.com/downloads](https://git-scm.com/downloads)

---

## 2. Procédure d Installation Détaillée sous WINDOWS (PowerShell)

### Étape 1 : Cloner le dépôt et ouvrir le dossier

Ouvrez un terminal **PowerShell** :

```powershell
git clone <repository-url>
cd axora
```

### Étape 2 : Créer et activer l environnement virtuel Python

```powershell
# Création de l environnement virtuel
python -m "venv" .venv

# Activation sous PowerShell
.\.venv\Scripts\Activate.ps1
```

> **Note de sécurité PowerShell :** Si vous obtenez une erreur du type *"L exécution de scripts est désactivée"*, exécutez d abord cette commande :
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

### Étape 3 : Installer les dépendances Python requises

```powershell
# Mettre à jour pip et installer toutes les dépendances
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 4 : Configurer la base de données PostgreSQL sous Windows

1. Ouvrez l outil **pgAdmin 4** ou **SQL Shell (psql)** fourni avec PostgreSQL.
2. Créez la base de données et l utilisateur :
   ```sql
   CREATE USER postgres WITH PASSWORD "postgres";
   CREATE DATABASE axora OWNER postgres;
   GRANT ALL PRIVILEGES ON DATABASE axora TO postgres;
   ```

### Étape 5 : Configurer le fichier `.env` sous Windows

Copiez le fichier exemple :

```powershell
Copy-Item .env.example .env
```

Éditez le fichier `.env` (ex: avec Notepad ou VS Code) et configurez les variables d accès local :

```env
# Configuration locale sans Docker (Windows)
PROJECT_NAME=Axora
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/axora

# Clés et modèle LLM
LLM_PROVIDER=openai
LLM_API_KEY=sk-proj-votre-cle-api-ici
LLM_MODEL=gpt-4o-mini
```

---

## 3. Procédure d Installation Détaillée sous LINUX (Ubuntu / Debian)

### Étape 1 : Installer les paquets système requis

Ouvrez votre terminal Linux :

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip postgresql postgresql-contrib git
```

### Étape 2 : Configurer PostgreSQL local sous Linux

```bash
# Démarrer le service PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Se connecter en tant qu utilisateur postgres pour créer la base et l utilisateur
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres';"
sudo -u postgres psql -c "CREATE DATABASE axora OWNER postgres;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE axora TO postgres;"
```

### Étape 3 : Cloner le projet et configurer l environnement

```bash
git clone <repository-url>
cd axora

# Créer et activer l environnement virtuel
python3 -m "venv" .venv
source .venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 4 : Configurer le fichier `.env` sous Linux

```bash
cp .env.example .env
```

Éditez `.env` pour cibler `localhost` :

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/axora
LLM_PROVIDER=openai
LLM_API_KEY=sk-proj-votre-cle-api-ici
```

---

## 4. Guide de Lancement et Démarrage de l Application

Une fois l installation terminée (environnement virtuel active), vous disposez de deux modes d exécution :

### Mode A : Lancer le Serveur API HTTP FastAPI

#### Windows (PowerShell) :
```powershell
$env:PYTHONPATH="src"
uvicorn axora.main:app --reload --host 127.0.0.1 --port 8000
```

#### Linux (Bash) :
```bash
PYTHONPATH=src uvicorn axora.main:app --reload --host 127.0.0.1 --port 8000
```

- **Lien Swagger UI :** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check :** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### Mode B : Lancer l Interface Interactive Terminal CLI

L interface CLI interactive vous permet de dialoguer directement avec l agent Axora depuis votre terminal local :

#### Windows (PowerShell) :
```powershell
$env:PYTHONPATH="src"
python -m axora.cli
```

#### Linux (Bash) :
```bash
PYTHONPATH=src python3 -m axora.cli
```

---

## 5. Exécution de la Suite de Tests Unitaires en Local

Pour vérifier que tout fonctionne parfaitement sur votre machine locale :

#### Windows (PowerShell) :
```powershell
$env:PYTHONPATH="src"
pytest
```

#### Linux (Bash) :
```bash
PYTHONPATH=src pytest
```

---

**Axora — From intent to action.**
