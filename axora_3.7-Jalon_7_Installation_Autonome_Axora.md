# AXORA - Jalon 7 : Installation Autonome et Préparation de l'Environnement

> **Spécification d'Implémentation (v3.7)**  
> **Statut :** Prêt pour implémentation, sous réserve de validation des décisions de périmètre  
> *Permettre à un client non technique de lancer l'installation d'Axora et laisser le bootstrapper puis l'agent préparer et vérifier l'application et sa base.*

---

## 1. Vision du Jalon

Un client demande l'installation d'Axora sans connaître les prérequis. Il lance un bootstrapper local, décrit le résultat souhaité et ne répond qu'aux décisions nécessaires : type d'installation, fournisseur IA, éventuels secrets et autorisations d'administration.

Le système :

1. détecte l'environnement et ses capacités ;
2. choisit un parcours pris en charge ;
3. prépare les dépendances et les services Axora ;
4. prépare ou vérifie la base de données ;
5. configure le fournisseur LLM choisi ;
6. démarre Axora, vérifie son état, puis explique le résultat dans des termes compréhensibles.

« Autonome » signifie que le système orchestre les étapes techniques déjà autorisées. Il ne contourne pas les permissions OS, les politiques de l'entreprise ou le consentement concernant les données.

---

## 2. Principe d'Amorçage

Axora ne peut pas installer ses propres prérequis avant d'être lancée. Le Jalon 7 comprend donc deux composants distincts :

### 2.1 Bootstrapper local

Petit point d'entrée sans dépendance au runtime conversationnel complet. Il détecte l'OS, valide le support, contrôle Docker/Compose ou les prérequis du mode choisi et démarre le parcours d'installation. Il ne donne pas implicitement accès au daemon Docker.

### 2.2 Assistant de configuration Axora

Une fois démarrée dans un mode de configuration guidée, l'application reprend l'état du bootstrapper, pose les questions non techniques, orchestre les étapes autorisées, puis fournit le rapport final.

Un processus Axora exécuté dans un conteneur ne prétend pas contrôler l'hôte. Toute action sur l'hôte est réalisée par le bootstrapper explicitement lancé et autorisé par le client.

---

## 3. Périmètre de la Première Livraison

### Inclus : parcours « Démonstration locale - Docker Compose »

- **OS cible initial recommandé :** Ubuntu/Debian Linux avec Docker Engine et le plugin Compose déjà installé et accessible.
- Détection Docker CLI, daemon, Compose, ressources minimales et contexte hôte/conteneur.
- Vérification de la configuration Compose du dépôt et inventaire limité au projet Axora.
- Création d'une configuration locale à partir de valeurs par défaut sûres ; secrets générés localement, jamais fournis par le LLM.
- Démarrage des services nécessaires à la démonstration : API et PostgreSQL ; outils annexes désactivables.
- Attente du healthcheck réel de PostgreSQL, application du schéma Axora sur une base neuve et test de connexion API/DB.
- Fournisseur LLM configuré par l'utilisateur, ou mode de démonstration explicitement limité sans fournisseur distant.
- Rapport récapitulatif et reprise après interruption.
- Mode « plan » sans mutation avant le premier démarrage.

### Non inclus dans la première livraison

- Installation silencieuse de Docker ou d'un daemon OS par Axora.
- Installation Windows/macOS ou toutes distributions Linux.
- Provisionnement Kubernetes ou cloud.
- Connexion guidée à tous les SGBD pluggables ; utiliser une base externe relève d'un lot ultérieur.
- Mise à jour, désinstallation ou nettoyage destructif des installations.
- Seed de données de démonstration automatique par défaut.
- Utilisation de l'API distante comme canal de contrôle de l'hôte.

Si Docker est absent ou inaccessible, le bootstrapper explique le blocage, indique la démarche adaptée et reprend le parcours après installation manuelle. Aucune commande `sudo` n'est lancée automatiquement.

---

## 4. Parcours Client Cible

```text
Client      : Je veux essayer Axora.
Bootstrapper: Cette machine est compatible. Docker est installé et accessible.
              Je peux démarrer Axora et une base locale isolée.
Client      : D'accord.
Axora       : Voulez-vous activer les réponses IA ? Choisissez un fournisseur
              ou continuer en mode démo sans fournisseur distant.
Client      : J'active mon fournisseur. [Saisit la clé dans un champ secret local.]
Axora       : Je vais créer une nouvelle base de démonstration, préparer son schéma
              et démarrer l'API. Aucune base existante ne sera modifiée.
Client      : Confirmer.
Axora       : Installation prête. L'API, la base et la connexion IA ont été vérifiées.
```

Le parcours conserve les paramètres et l'étape atteinte pour permettre de reprendre après fermeture, redémarrage ou panne réseau.

---

## 5. Architecture Cible

```text
installer/
└── bootstrapper/                 # Entrée locale, détection et orchestration initiale

src/axora/extensions/environment/
├── models.py                      # Profil, rapport, étapes et état d'installation
├── detector.py                    # OS, ressources et contexte d'exécution
├── planner.py                     # Plan explicite, sans effet de bord
├── executor.py                    # Exécution bornée et reprise
├── state_store.py                 # État local sans secrets
├── docker/
│   ├── client.py                  # Opérations Docker autorisées
│   └── compose_inspector.py       # Validation et inventaire Compose
├── database/
│   ├── provisioner.py             # Base locale du profil démonstration
│   └── readiness.py               # Connectivité et readiness du schéma
└── llm/
    └── setup.py                   # Choix fournisseur et vérification sécurisée

src/axora/                         # Configuration guidée, readiness et rapport
tests/
└── test_environment_setup.py      # Mocks OS/Docker/DB/LLM et parcours de reprise
```

Les commandes système sont construites par des composants Python déterministes à partir d'une liste d'actions autorisées. Aucune commande arbitraire issue du LLM n'est exécutée.

---

## 6. Lots d'Implémentation

### Lot 0 - Fiabiliser le déploiement Axora

**Objectif :** garantir que le déploiement actuel fonctionne avant de l'automatiser.

- [x] Corriger l'URL API vers PostgreSQL au port interne `5432` et exiger les paramètres de connexion nécessaires.
- [x] Utiliser `/health/ready` comme healthcheck API ; cette route vérifie réellement la connexion PostgreSQL.
- [x] Déplacer pgAdmin derrière le profil `admin`, retirer ses credentials de développement et limiter son port à localhost.
- [x] Retirer les mots de passe fixes du service MySQL optionnel, limiter son port à localhost et corriger son healthcheck.
- [x] Configurer le profil LLM d'exemple sur `mock`, vider les clés API fictives et rendre le mot de passe PostgreSQL obligatoire.
- [x] Activer l'utilisateur non-root dans l'image applicative.
- [x] Ajouter les tests unitaires de readiness et des invariants de configuration Compose.
- [x] Ajouter au CI le build Docker et la validation Compose.
- [x] Valider localement le build Docker et `docker compose config` sans lire le `.env` du workspace.
- [ ] Exécuter un démarrage Compose complet en CI et tester une installation de bout en bout.
- [ ] Séparer les profils Compose `demo` et `production`, et fixer une politique de pinning des images.

**État du lot :** première tranche réalisée ; le démarrage Compose complet et le profil production restent à valider avant de déclarer le lot terminé.

**Validation locale :**

```bash
PYTHONPATH=src python -m pytest tests/test_health.py tests/test_deployment_config.py
docker build --tag axora:local .
```

Résultats de cette tranche : **10 tests ciblés passent**, build de l'image réussi et configuration Compose valide. Le démarrage de services Compose n'a pas été lancé ; le test d'intégration avec DB réelle reste à faire.

### Lot 1 - Inventaire et plan en lecture seule

- Détecter la distribution Linux, l'architecture, les ressources et si le processus courant est conteneurisé.
- Détecter Docker CLI, daemon accessible, version Compose et contexte Docker sans afficher de configuration secrète.
- Vérifier la compatibilité et le chemin du projet Axora.
- Valider le Compose résolu sans imprimer sa sortie avec valeurs sensibles.
- Inspecter seulement les ressources associées au projet Axora.
- Générer un plan lisible : actions, services, ports, volumes persistants, prérequis, risques et demandes d'autorisation.
- Ajouter `axora install --check` et `axora install --plan`.

**Critère de sortie :** les scénarios Docker absent, daemon arrêté, permission refusée, environnement compatible sont différenciés ; le plan ne lance aucune mutation.

### Lot 2 - Bootstrapper et démarrage local

- Fournir une commande/entrée d'installation adaptée au premier OS retenu.
- Préparer uniquement les fichiers Axora appartenant au répertoire d'installation.
- Créer une configuration locale avec permissions de fichier restrictives.
- Démarrer seulement les services nécessaires au profil `demo`.
- Ne jamais réinitialiser ni supprimer un volume existant.
- Afficher les droits manquants et instructions requises ; aucune élévation automatique.

**Critère de sortie :** un client peut lancer l'installation sur un poste prérequis, comprendre les demandes et démarrer une instance Axora neuve.

### Lot 3 - Base de données, schéma et reprise

- Attendre la disponibilité réelle de PostgreSQL via healthcheck et connexion applicative.
- Distinguer une base neuve d'une base existante avant toute écriture.
- Pour la base neuve créée par le profil `demo`, appliquer le manifeste et vérifier les tables attendues.
- Pour toute base existante, s'arrêter à l'inspection et au diff ; demander une approbation explicite avant migration.
- Ne pas exécuter de seed par défaut ; le jeu de démo éventuel est opt-in et limité à une base neuve.
- Persister les étapes complétées, erreurs et tentatives sans enregistrer mots de passe ni tokens.
- Rendre chaque étape idempotente et reprendre après interruption sans opérations destructives.

**Critère de sortie :** une panne/reprise ne duplique pas les étapes ou données et ne modifie pas une base existante sans accord explicite.

### Lot 4 - Fournisseur LLM et readiness complète

- Demander le fournisseur, le modèle et la politique de connectivité en langage simple.
- Accepter la clé via un champ sécurisé local ; elle ne transite jamais dans le prompt, les arguments du tool ou les logs.
- Offrir un mode limité sans fournisseur distant, clairement présenté comme tel.
- Tester la connectivité et l'authentification sans transmettre de données métier.
- Ajouter une readiness qui distingue API, DB, schéma et LLM ; ne pas assimiler `/health` process-only à une installation prête.
- Présenter un récapitulatif des URLs locales et de l'état, sans secrets.

**Critère de sortie :** le rapport final expose exactement les composants opérationnels et les limitations restantes.

### Lot 5 - Intégration de l'agent et extension de plateformes

- Permettre à l'agent d'expliquer le diagnostic et de poursuivre les actions déjà autorisées.
- Ajouter les plateformes/modes suivants uniquement après tests d'installation dédiés : Windows/Docker Desktop, autres distributions Linux, base externe, installation native.
- Ajouter une interface web de consentement seulement si elle peut confirmer l'action et son plan exact.

**Critère de sortie :** chaque plateforme annoncée prise en charge passe un test d'installation bout en bout ; les autres sont explicitement refusées avec une procédure claire.

---

## 7. Politique de Consentement et Sécurité

| Action | Politique initiale |
|---|---|
| Détection OS/outils et validation de configuration | Automatique, lecture seule |
| Inspection des ressources Axora uniquement | Automatique, lecture seule |
| Téléchargement d'image/dépendance | Après présentation du plan et accord d'installation |
| Démarrage de conteneurs et création de volume Axora | Confirmation explicite la première fois |
| Génération de secrets locaux | Automatique, jamais affichée ou envoyée au LLM |
| Saisie de clé LLM | Saisie directe par l'utilisateur dans un champ secret |
| Migration d'une base existante | Diff et sauvegarde proposés, approbation explicite obligatoire |
| Seed de démonstration | Désactivé par défaut ; opt-in, base neuve uniquement |
| Installation système nécessitant des droits admin | Instructions ou mécanisme OS avec accord explicite ; pas de `sudo` automatique |
| Suppression de données, volumes ou ressources | Hors périmètre |

Une confirmation est liée à un plan précis, à sa version/configuration et à ses effets. Une approbation précédente ne vaut pas autorisation permanente.

---

## 8. État d'Installation et Rapport Final

L'état local peut contenir :

- identifiant d'installation et profil ;
- version Axora et empreinte non secrète de la configuration ;
- étapes réussies, étape en cours, temps et résultat ;
- noms des services/ressources Axora gérés ;
- consentements associés à un plan ;
- étapes de reprise et erreurs expurgées.

Il ne contient jamais :

- clé API, mot de passe, token ou URL avec identifiants ;
- copie du `.env` ;
- dump de base, données métier ou logs complets par défaut.

Le rapport final présente : statut global, état API/DB/schéma/LLM, chemins et URL utiles, profil activé, actions restant au client, et instructions de reprise/support.

---

## 9. Stratégie de Test et Critères d'Acceptation

### Tests unitaires

- OS/outils/versions/support détectés avec fournisseurs simulés ;
- Docker manquant, daemon inaccessible, refus de permission, timeout ;
- génération et redaction de configuration/secrets ;
- plan sans effet de bord ;
- état d'installation persistant et reprise idempotente ;
- DB neuve vs existante, migration en attente d'approbation, seed opt-in ;
- healthchecks indépendants API/DB/schéma/LLM.

### Tests d'intégration

- démarrage du Compose sur un runner isolé ;
- attente de PostgreSQL et readiness API ;
- migration sur DB neuve et vérification des tables ;
- interruption puis reprise du parcours ;
- validation qu'aucune donnée existante n'est supprimée.

### Acceptation utilisateur

- Le client non technique sait démarrer le bootstrapper et répondre aux seules décisions pertinentes.
- Si un prérequis privilégié est absent, Axora explique exactement le blocage et reprend après correction.
- L'installation ne divulgue aucun secret et ne lit pas le contenu du `.env`.
- Une base existante n'est jamais modifiée sans approbation de migration.
- Le message « prêt » n'est affiché que si les vérifications requises du profil choisi réussissent.
- Les scénarios d'échec offrent une reprise ou un rapport exploitable, jamais un succès de façade.

---

## 10. Décisions de Périmètre Recommandées

Pour lancer l'implémentation, les valeurs par défaut proposées sont :

1. **Plateforme initiale :** Ubuntu/Debian Linux avec Docker/Compose déjà installé.
2. **Profil initial :** démonstration locale avec PostgreSQL neuf isolé et sans seed par défaut.
3. **Docker manquant :** le bootstrapper n'installe pas de moteur privilégié ; il guide le client et reprend ensuite.
4. **LLM :** fournisseur externe sélectionné par le client, ou mode limité sans fournisseur distant ; clé saisie hors conversation.
5. **Base existante :** détection et plan seulement ; aucune migration sans diff, sauvegarde et accord.
6. **Consentement :** demande explicite lors du premier démarrage des ressources Axora.
7. **Ordre de travail :** lots 0 à 4 avant d'annoncer l'installation autonome ; lot 5 séparé.

Ces décisions constituent le périmètre de référence pour l'implémentation, sauf choix contraire du responsable produit.

---

## 11. Constats Techniques à Traiter

1. Le [guide d'installation local](./axora_1.0-Guide_Installation_Local_Sans_Docker_Windows_Linux.md) suppose l'installation et la configuration manuelles des dépendances, de PostgreSQL et du fournisseur LLM.
2. Le [compose.yaml](./compose.yaml) définit PostgreSQL sur son port interne standard, alors que l'URL injectée dans l'API vise actuellement un autre port interne. Le lot 0 doit corriger et tester cette configuration.
3. Le Compose contient des valeurs de développement pour certains services. Elles ne constituent pas une configuration de production sûre et doivent être remplacées ou désactivées dans les profils d'installation.
4. Le [moteur de migration](./src/axora/data/migrations.py) cible aujourd'hui un manifeste par défaut et n'offre pas de plan/approbation pour une base existante. Il doit être rendu explicite et sûr avant son automatisation.
5. Le seed crée des données d'exemple et ne doit pas être exécuté silencieusement pour un nouveau client, encore moins sur sa base existante.
6. Le healthcheck API actuel prouve principalement que le processus HTTP répond ; il doit être distingué de la readiness DB/schéma/LLM.
7. Le choix du fournisseur LLM et ses secrets sont des entrées client ; l'agent ne peut pas les deviner ni les inclure dans ses prompts.

Ces éléments sont des travaux à réaliser ; ce document ne prétend pas qu'ils sont déjà corrigés.

---

## 12. Hors Périmètre de ce Document

Ce jalon est prêt à être découpé en tâches, mais aucun changement d'exécution, installation Docker, migration, seed ou modification de configuration n'est réalisé par cette spécification. Les travaux de code commencent après validation du périmètre produit et du premier OS cible.
