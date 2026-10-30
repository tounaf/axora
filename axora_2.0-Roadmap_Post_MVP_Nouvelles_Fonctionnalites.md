# AXORA — Feuille de Route Post-MVP & Nouvelles Fonctionnalités v2.0

> **Document de vision produit et spécifications techniques post-MVP.**
> *Passage de la preuve de concept CLI/Chat à une plateforme d'intelligence décisionnelle d'entreprise.*

---

## 🚀 1. Synthèse du Succès du MVP v1.0
Le MVP d'Axora a validé avec succès l'architecture fondamentale **Intent-to-Action** :
- **Sémantique dynamique** : Moteur fonctionnant directement à partir du manifeste YAML (`gestion_paroissiale.yaml`) sans entités ni colonnes figées dans le code.
- **Support Multi-LLM** : Adaptateurs ultra-rapides pour **Groq LPU** (`llama-3.3-70b-versatile`, `openai/gpt-oss-120b`), **NVIDIA NIM**, et **OpenAI**.
- **Moteur de Requête & Mutation** : Traitement SQL dynamique avec résolution automatique des relations N-1, 1-N et N-N (tables de jonction).
- **Interface CLI Interactive & API Chat** : Boucle d'agent autonome avec mécanisme de récupération automatique et tolérance aux pannes (`failed_generation`).

---

## 🎯 2. Axes de Développement Post-MVP (Feuille de Route)

### FEAT-08 — Interface Web Moderne & Tableaux de Bord Interactifs (Next.js / Tailwind)
- **Description** : Déploiement d'un Web UI responsive intégrant un widget de chat d'agent conversationnel, la visualisation graphique des entités et des dashboards analytiques.
- **Fonctionnalités** :
  - **Chatbot interactif** avec rendu Markdown, tableaux interactifs et export de graphiques en un clic.
  - **Explorateur de Modèle Sémantique** : Visualisation sous forme de graphe dynamique (React Flow) des entités, attributs et relations.
  - **Tableau de bord Paroissial** : Widgets générés dynamiquement par l'agent en fonction des données filtrées.

---

### FEAT-09 — Canaux de Communication Multi-Canaux (WhatsApp, Telegram, Slack, Email)
- **Description** : Permettre aux gestionnaires, pasteurs et membres d'interagir avec l'Agent Axora directement depuis leurs applications de messagerie quotidiennes.
- **Fonctionnalités** :
  - **Bot WhatsApp & Telegram** (via Twilio / Telegram Bot API) :
    - *Exemple d'usage* : Un responsable de zone envoie un message vocal ou texte : *"Donne-moi la liste des jeunes de ma zone"*.
  - **Intégration Slack / Microsoft Teams** pour la gestion administrative et les notifications de groupe.
  - **Rapports Email Hebdomadaires** : Résumé automatique envoyé par l'agent aux dirigeants (statistiques d'adhésion, transferts approuvés).

---

### FEAT-10 — Moteur Multi-Tenancy & Sécurité RBAC (Role-Based Access Control)
- **Description** : Support de plusieurs paroisses/organisations isolées avec contrôle d'accès strict selon le rôle de l'utilisateur.
- **Fonctionnalités** :
  - **Multi-Tenancy étanche** : Isolation au niveau de la base de données (`tenant_id` dynamique injecté dans toutes les requêtes).
  - **Rôles & Permissions granulaires** :
    - *Administrateur Général* : Accès à l'ensemble du réseau paroissial.
    - *Pasteur / Secrétaire de Paroisse* : Lecture/Écriture limitée à sa paroisse.
    - *Chef de Zone / Association* : Accès restreint à ses membres uniquement.
  - **Sécurité Sémantique** : L'Agent filtre automatiquement les données accessibles en fonction du token JWT de l'utilisateur connecté.

---

### FEAT-11 — Moteur d'Agrégation Avancé & Génération de Rapports (PDF / Excel / CSV)
- **Description** : Étendre le `QueryEngine` pour prendre en charge les agrégations complexes (`COUNT`, `SUM`, `AVG`, `GROUP BY`) et générer des documents officiels.
- **Fonctionnalités** :
  - **Requêtes d'Agrégation Avancées** : *"Donne-moi la moyenne d'âge des membres par association et par paroisse"*.
  - **Génération de Fiches & Certificats PDF** :
    - Génération automatique d'Attestations de Transfert (Passage), Certificats de Membre, et Registres Paroissiaux.
  - **Exportation Dynamique** : Export des résultats de recherche au format Excel (`.xlsx`) ou CSV en un simple ordre conversationnel.

---

### FEAT-12 — Notifications Proactives & Déclencheurs d'Événements Métier (Event-Driven Agent)
- **Description** : L'Agent ne se contente plus de répondre aux questions, il surveille la base de données et prend des initiatives proactives.
- **Fonctionnalités** :
  - **Alertes d'Anniversaires et de Fêtes** : Notification quotidienne au secrétaire avec les anniversaires du jour.
  - **Application Automatique des Règles Métier (BR-003, BR-004, BR-005)** :
    - Détection automatique lorsqu'un membre atteint l'âge de 16 ans -> Suggestion d'adhésion à l'Association des Jeunes.
  - **Rappels de Suivi** : Notification lorsqu'une Demande de Passage est en attente d'approbation depuis plus de 7 jours.

---

### FEAT-13 — Agent Vocologique (Voice Intent Channel STT/TTS)
- **Description** : Intégration de la reconnaissance et synthèse vocale pour permettre des interactions 100% vocales en langue naturelle (Français, Malgache, Anglais).
- **Fonctionnalités** :
  - **Speech-to-Text (Whisper / Groq Voice API)** : Transcription instantanée des messages vocaux des utilisateurs.
  - **Text-to-Speech (ElevenLabs / Piper TTS)** : Réponse vocale naturelle de l'agent.

---

### FEAT-14 — RAG Vectoriel & Recherche Documentaire Non Structurée
- **Description** : Associer la base de données relationnelle à un Moteur RAG (Retrieval-Augmented Generation) sur base vectorielle (pgvector / Qdrant).
- **Fonctionnalités** :
  - **Recherche dans les Règlements & Canon Pastoral** : L'agent répond aux questions de droit ou procédure paroissiale (*"Quelle est la procédure officielle pour organiser un baptême ?"*).
  - **Indexation des Procès-Verbaux de Réunion** : Recherche sémantique dans l'historique des PV de comités paroissiaux.

---

### FEAT-15 — Traçabilité, Audit & Observabilité Enterprise (OpenTelemetry / LangSmith)
- **Description** : Journalisation exhaustive des décisions de l'agent et historique des modifications de la base de données.
- **Fonctionnalités** :
  - **Audit Trail Complet** : Enregistrement de qui a modifié quoi, quand, et via quelle intention d'agent.
  - **Observabilité des Appels LLM** : Suivi du coût en tokens, du temps de latence et des taux de succès des adaptateurs LLM (Groq/NVIDIA/OpenAI).

---

## 🗓️ 3. Feuille de Route Temporelle Recommandée

| Phase | Horizon | Objectif Principal | Livrables Clés |
|---|---|---|---|
| **Phase 1** | Q1 (Mois 1-2) | **Sécurité & Multi-Tenancy** | RBAC, Isolement Tenant, Filtres Sémantiques par rôle |
| **Phase 2** | Q2 (Mois 3-4) | **Web UI & Agrégations** | Interface Dashboard Next.js, Exports PDF/Excel, Agrégations SQL |
| **Phase 3** | Q3 (Mois 5-6) | **Multi-Canaux & Proactivité** | Bot WhatsApp/Telegram, Notifications d'Événements, Moteur BR Automatique |
| **Phase 4** | Q4 (Mois 7-8) | **RAG Documentaire & Voice** | Intégration pgvector, Recherche Canon/PV, Canal Vocal STT/TTS |

---

*Feuille de route générée pour la plateforme Axora v2.0.*
