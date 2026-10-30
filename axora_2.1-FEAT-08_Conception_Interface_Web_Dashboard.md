# AXORA — Conception Technique FEAT-08 : Interface Web Dashboard & Assistant Interactif

> **Document de Conception Architecturelle & Ergonomique Front-End (Spécification FEAT-08)**
> *Basé sur le modèle visuel et d'expérience utilisateur Stitch "Axora - Assistant Données Métier" (`07beec81280e427588c6f2475817b60a`).*

---

## 🎯 1. Objectifs & Définition du FEAT-08

Le module **FEAT-08** fait passer Axora de l'interface en ligne de commande (CLI) à une **application web interactive d'entreprise** complète.
L'application offre aux utilisateurs métier (pasteurs, secrétaires de paroisse, gestionnaires d'association) et aux administrateurs informatiques un cockpit à 3 colonnes pour interagir en langage naturel avec le système d'information.

---

## 📐 2. Architecture Globale de l'Interface (Layout à 3 Colonnes)

L'interface web adopte une disposition ergonomique à haute densité d'information articulée autour de 3 composants principaux :

```
+---------------------------------------------------------------------------------------------------------+
|                                              HEADER TOP BAR                                             |
|  [Mode Agent] [Domaine: Gestion paroissiale v]                      [Thème] [JD - Jean Dupont v]        |
+------------------+----------------------------------------------------+---------------------------------+
| SIDEBAR GAUCHE   | ZONE DE CHAT CENTRALE                              | PANNEAU INSPECTEUR DROIT        |
| (w-64)           | (flex-1)                                           | (w-80)                          |
|                  |                                                    |                                 |
| Axora Logo       |  Assistant Axora                                   | [Contexte] [Outils] [Mémoire]   |
| "From intent..." |  Posez vos questions en langage naturel...         |                                 |
|                  |                                                    | 💡 Résumé de la requête        |
| 💬 Assistant     | 👤 User: Liste les membres...                      |    Obtenir la liste des membres |
| 🔗 Modèle métier |                                                    |                                 |
| 📊 Données       | 🤖 Axora Agent:                                    | 🧩 Concepts mobilisés            |
| 🛠️ Outils        |    ✅ Step 1: Analyse de la demande                |    - Paroisse (canonique)       |
| 📜 Historique    |    🛠️ Step 2: Outils utilisés (discover_model,     |    - Membre (canonique)         |
| ⚙️ Paramètres    |                query_data)                         |                                 |
|                  |    📊 Step 3: Résultat & Tableau Dynamique           | 🗄️ Données consultées          |
|                  |    ⚡ Actions Rapides ([Export CSV], [Zones])      |    Tables: paroisse, membre     |
| Status Systèmes  |                                                    |                                 |
| 🟢 API • DB • LLM| 💬 [Barre de Saisie Message ...] [Envoyer]          | 🛡️ Règles Métier Appliquées    |
+------------------+----------------------------------------------------+---------------------------------+
```

---

## 🎨 3. Spécification des Composants Front-End

### 3.1 Sidebar Navigational Gauche (`SidebarNav.tsx`)
- **Dimensions & Style** : Largeur fixe `256px` (`w-64`), fond obscur sombre `#081528` (`bg-brand-sidebar`).
- **Éléments** :
  1. **En-tête Branding** : Logo dégradé de bleu (`#1d4ed8` vers `#38bdf8`) avec icône géométrique A et baseline *"From intent to action."*.
  2. **Menu de Navigation** :
     - `Assistant` (*Actif* - fond bleu `#1a56db`)
     - `Modèle métier` (Visualisateur de graphe YAML avec React Flow)
     - `Données` (Explorateur de tables et enregistrements SQL)
     - `Outils` (Registre des outils de l'agent : `discover_model`, `query_data`, etc.)
     - `Historique` (Persistance des conversations par session UUID)
     - `Paramètres` (Choix du provider LLM : Groq, NVIDIA NIM, OpenAI, Ollama)
  3. **Cartouche de Santé Système (Footer Sidebar)** :
     - Indicateur d'état en temps réel avec puce verte pulsante (`animate-ping`).
     - *"Système opérationnel • API • Base de données • LLM"*.

---

### 3.2 Barre Supérieure Header (`TopHeader.tsx`)
- **Hauteur & Style** : Largeur fluide, hauteur `56px` (`h-14`), fond blanc pur avec bordure inférieure `border-slate-200`.
- **Composants** :
  - **Badge Mode Agent** : Pilule bleue rétro-éclairée (`Mode Agent` avec icône d'étoile spark).
  - **Sélecteur de Domaine Métier** : Menu déroulant interactif pour basculer de modèle sémantique (`Gestion paroissiale v0.2`).
  - **Commutateur de Thème** (Mode Sombre / Clair).
  - **Profil Utilisateur & Avatar** : Avatar circulaire initiales (`JD - Jean Dupont`).

---

### 3.3 Canvas Chat & Résultats Interactifs (`ChatCanvas.tsx`)
- **Structure** : Flux vertical défilable sans saccade avec défilement doux (`custom-scrollbars`).
- **Composants d'Interaction** :
  1. **Bulles de Message Utilisateur** : Alignées à droite, fond bleu doux (`#eff6ff`), bordure fine, horodatage et coche de confirmation d'envoi.
  2. **Cartes d'Exécution de l'Agent Axora** :
     - **Étape 1 : Analyse de l'Intention** (Badge vert d'analyse validée).
     - **Étape 2 : Accordéon d'Outils Invoqués** :
       - Affiche la liste des outils appelés par la boucle d'exécution (ex. `discover_model`, `query_data`).
       - Puce de statut d'exécution (`Succès` / `Erreur`) et arguments passés au format JSON.
     - **Étape 3 : Rendu des Résultats** :
       - **Tableaux de Données Dynamiques** : Rendu des enregistrements retournés par le `QueryEngine` sous forme de tableau responsive avec tri de colonnes et badges d'état (`Actif`, `CELIBATAIRE`, etc.).
       - **Puces d'Actions Rapides Contextuelles** : Boutons de raccourcis générés automatiquement (ex : `[Voir les zones]`, `[Export CSV]`, `[Infos Paroisse]`).
  3. **Barre de Saisie Flottante (Bottom Input Bar)** :
     - Champ texte arrondi avec ombre douce, bouton d'attachement de fichier/document et bouton d'envoi rapide.

---

### 3.4 Panneau Inspecteur Contextuel Droit (`ContextInspector.tsx`)
- **Dimensions & Style** : Largeur fixe `320px` (`w-80`), fond blanc avec séparation verticale `border-l`.
- **Onglets Supérieurs** : `Contexte` | `Outils` | `Mémoire`.
- **Cartes d'Inspection Dynamiques** :
  1. **Résumé de la requête** : Reformulation claire de l'intention métier par l'agent.
  2. **Concepts mobilisés** : Entités canoniques identifiées (ex : `Paroisse`, `Membre`) et leurs synonymes.
  3. **Données consultées** :
     - Tables SQL interrogées (`paroisse`, `membre`, `zone_geographique`).
     - Jointures SQL générées dynamiquement par le `QueryEngine` (ex : `membre.paroisse_id → paroisse.id`).
  4. **Règles Métier Appliquées** : Rappel des règles du domaine impliquées (ex : BR-001, BR-003).
  5. **Métriques Techniques** : Modèle sémantique utilisé (`gestion_paroissiale v0.2`), temps de réponse (`1.24s`), moteur de base de données (`PostgreSQL 17`).

---

## 🛠️ 4. Stack Technique & Intégration API

### 4.1 Technologies Front-End Recommandées
- **Framework** : Next.js 14+ (App Router, TypeScript)
- **Styling** : Tailwind CSS v3.4+
- **Composants UI** : Radix UI / Shadcn UI
- **Graphe Sémantique** : React Flow (pour l'explorateur du modèle métier)
- **State Management** : Zustand / TanStack Query (React Query v5)

### 4.2 Contrat d'API REST / Stream (FastAPI Backend)
L'interface web communique directement avec l'API FastAPI d'Axora (`src/axora/api/routes.py`) :
- `POST /api/v1/chat/completions` : Envoi des intentions utilisateur avec réponse structurée JSON comprenant :
  - `response` : Texte ou Markdown de réponse finale.
  - `steps` : Historique des décisions d'agent et des outils exécutés (`discover_model`, `query_data`).
  - `context_inspector` : Payload d'inspection (concepts, tables, jointures, règles métier).

---

*Document de conception établi pour le développement du module FEAT-08 d'Axora.*
