# Axora — v3.8 : Suivi de progression de l'agent et des parcours

**Statut :** Implémenté et validé  
**Périmètre :** WebUI, API, CLI conversationnel, bootstrap et installation d'Axora

---

## 1. Objectif

Rendre visible l'avancement d'Axora pendant le traitement d'une demande et pendant les parcours d'initialisation ou d'installation. L'utilisateur doit pouvoir distinguer les étapes terminées, l'étape en cours, la réussite et l'échec, quel que soit le canal utilisé.

Le terme « thinking » désigne ici des **indications d'avancement compréhensibles**, et non la chaîne de pensée du modèle. Axora ne doit pas exposer les raisonnements internes du LLM, les prompts, les arguments bruts d'outils, les résultats internes non filtrés, les secrets ou les données personnelles.

## 2. Canaux couverts

| Canal | Comportement attendu |
|---|---|
| WebUI | Afficher en direct l'étape courante de l'agent, puis la réponse finale ou une erreur explicite. |
| API | Fournir un endpoint de flux d'événements pour les clients qui ont besoin d'un avancement en direct. Préserver le contrat synchrone existant. |
| CLI conversationnel | Afficher des libellés lisibles pendant chaque traitement : analyse, outil en cours, résultat d'étape, réponse finale ou échec. |
| Bootstrap / démarrage | Signaler les étapes significatives d'initialisation (configuration, modèle sémantique, outils, runtime et disponibilité), avec échec visible si le démarrage ne peut pas aboutir. |
| Installation d'Axora | Signaler les étapes du parcours d'installation (validation, prérequis, démarrage des services, disponibilité, import/introspection et configuration), sans afficher de secrets ni de sortie brute sensible. |

Le bootstrap et l'installation ne doivent pas être présentés comme une réflexion du LLM : ils publient des états de cycle de vie, selon le même contrat d'événement.

## 3. Contrat commun d'événement

Chaque mise à jour est un événement structuré, transporté par le canal concerné :

| Champ | Sens |
|---|---|
| `type` | `progress`, `completed` ou `error`. |
| `phase` | Étape stable et exploitable par machine, par exemple `analysis`, `tool_execution`, `bootstrap` ou `installation`. |
| `status` | Pour un jalon : `started`, `completed` ou `failed`. |
| `message` | Libellé court, localisable et sûr pour l'utilisateur. |
| `tool` | Nom public de l'outil, facultatif et limité à une liste connue. |
| `iteration` | Numéro d'itération agentique et limite, facultatifs. |
| `timestamp` | Horodatage UTC de l'événement. |

Le contrat ne contient ni prompt ni raisonnement libre du LLM. Les messages sont produits par Axora à partir d'étapes connues, et non recopiés depuis les réponses intermédiaires du modèle.

Exemple conceptuel :

```json
{
  "type": "progress",
  "phase": "tool_execution",
  "message": "Recherche dans le modèle métier…",
  "tool": "discover_model",
  "iteration": 1,
  "timestamp": "2026-11-27T05:30:00Z"
}
```

Les étapes agentiques minimales sont :

1. Réception et analyse de la demande.
2. Attente de la décision du modèle.
3. Exécution de chaque outil, avec un début et un résultat (réussite ou erreur).
4. Génération de la réponse finale, ou demande de précision.
5. Fin de traitement ou échec explicite.

## 4. Architecture et transport

### 4.1 Runtime commun

La boucle agentique et le runtime publient les événements au moment où les étapes se produisent. Le mécanisme de notification est facultatif afin de conserver la compatibilité des appelants existants. Un appelant qui ne fournit pas de consommateur de progression continue à recevoir uniquement le résultat final.

Les événements de progression sont émis au fil de l'exécution, pas reconstruits après coup à partir des observations. Les erreurs d'outils restent transmises à l'agent pour sa correction éventuelle, mais l'interface indique les erreurs d'étape sans exposer de détails internes non filtrés.

### 4.2 API et WebUI

- Conserver `POST /api/v1/chat` et sa réponse JSON actuelle pour ne pas casser les clients existants.
- Ajouter `POST /api/v1/chat/stream`, sous forme d'événements serveur (SSE), qui émet les événements de progression puis un événement terminal contenant la réponse finale, l'identifiant de conversation et, le cas échéant, la vue associée.
- En cas d'échec, le flux se termine par un événement d'erreur explicite et le serveur ferme proprement le flux.
- La WebUI consomme le flux, affiche le dernier état reçu pendant l'attente, puis présente la réponse finale. Elle conserve l'affichage des vues et des erreurs réseau.
- Le flux doit rester associé à la conversation et à l'exécution qui l'a créé ; les requêtes simultanées ne doivent pas partager leurs événements ni leur contexte.

### 4.3 CLI

Le CLI conversationnel consomme les mêmes événements du runtime et les rend sous forme de messages concis dans le terminal. Chaque demande montre au minimum l'analyse, chaque outil effectivement exécuté et la fin. Les erreurs sont affichées clairement et ne doivent pas ressembler à une réussite.

Les commandes de bootstrap et d'installation rendent leurs propres étapes de cycle de vie dans le terminal, sans imprimer les secrets, les valeurs de configuration privée ou la sortie complète des sous-processus.

## 5. Bootstrap et installation

Le bootstrap publie les étapes réelles de préparation de l'application, sans annoncer une étape comme terminée avant sa réussite. Un échec de configuration ou d'initialisation est signalé et conserve le comportement d'échec existant.

Le parcours d'installation publie des jalons correspondant aux opérations déjà exécutées : validation du plan et des prérequis, préparation de l'état local, démarrage ou réutilisation des services, attente de disponibilité, import du dump si nécessaire, génération du manifeste et disponibilité de l'API. Les confirmations requises et les protections existantes (pas de suppression automatique, permissions privées, contrôle des cibles) restent inchangées.

Les étapes longues, notamment l'import, peuvent inclure un état d'attente ou une progression mesurable uniquement si la source de données fournit un pourcentage fiable. Aucun pourcentage ne doit être inventé.

## 6. Compatibilité, sécurité et qualité

- Les appelants existants du runtime et les réponses actuelles de `POST /api/v1/chat` restent compatibles.
- Tous les outils exécutés par la boucle utilisent le même mécanisme de progression, sans instrumentation spécifique à un outil.
- Les noms d'outils affichés sont contrôlés par Axora ; les arguments ne sont pas inclus dans les événements.
- Les erreurs techniques détaillées restent dans les journaux côté serveur. Les messages transmis au client ne révèlent pas les secrets, prompts, chaînes de connexion ou données sensibles.
- Les événements de progression ne sont pas persistés comme messages de conversation par défaut ; l'historique utilisateur conserve son contrat actuel.
- Les événements ne doivent pas induire en erreur : chaque état de fin correspond à une exécution réellement terminée.

## 7. Critères d'acceptation

1. Une exécution sans outil publie l'analyse, la génération de réponse et la fin.
2. Une exécution avec plusieurs outils montre chaque étape dans l'ordre et indique le résultat de chaque outil.
3. Une erreur d'outil ou une erreur de traitement est visible comme telle, sans être transformée en réussite.
4. Le endpoint synchrone conserve son schéma et son comportement historiques ; le endpoint de flux envoie les événements au fur et à mesure et termine par le résultat.
5. La WebUI met à jour son indicateur pendant une requête en cours et affiche correctement la réponse, la vue et les erreurs.
6. Le CLI affiche les événements du runtime sans changer le résultat conversationnel.
7. Le démarrage et l'installation présentent leurs jalons réels, y compris les échecs et les chemins de réutilisation.
8. Des traitements concurrents n'interfèrent pas entre eux et aucune donnée sensible n'apparaît dans les événements.
9. Les tests couvrent les producteurs du runtime, le contrat/flux API, l'affichage WebUI ou son adaptation testable, le CLI et les étapes d'installation concernées.

## 8. Plan d'implémentation

1. Définir le modèle d'événement de progression et un mécanisme de publication facultatif dans le runtime.
2. Émettre les événements de façon uniforme dans la boucle agentique et ajouter des tests d'ordre, de réussite et d'erreur.
3. Ajouter le flux API en conservant l'endpoint synchrone, puis faire consommer ce flux par la WebUI.
4. Brancher le CLI conversationnel et les parcours bootstrap/installation sur des messages de progression adaptés à leurs étapes réelles.
5. Compléter la documentation d'utilisation, lancer les tests ciblés et vérifier la compatibilité des parcours existants.

## 9. État d'implémentation et validation

L'ensemble des composants spécifiés a été implémenté et validé par tests automatisés :

| Composant | Fichiers sources | Rôle et validation |
|---|---|---|
| **Contrat d'événement** | `src/axora/progress.py` | Modèle Pydantic `ProgressEvent` et helper non-bloquant `publish_progress`. Testé unitairement dans `tests/test_progress.py`. |
| **Boucle Agent & Runtime** | `src/axora/agent/loop.py`, `src/axora/agent/runtime.py` | Émission d'événements de cycle de vie (`analysis`, `tool_execution`, `response`, `clarification`, `agent`). Masquage strict des arguments bruts et des prompts. |
| **API SSE & Rétrocompatibilité** | `src/axora/api/routes.py` | Ajout de `POST /api/v1/chat/stream` en Server-Sent Events tout en conservant `POST /api/v1/chat` synchrone. Gestion d'erreurs et isolation des requêtes concurrentes testées dans `tests/test_progress.py`. |
| **WebUI Réactive** | `web/src/components/ChatCanvas.tsx` | Consommation du flux SSE via `ReadableStream`, affichage dynamique du statut d'avancement sous forme de pastille animée, et rendu de la réponse finale et de la vue. Build Next.js validé. |
| **CLI & Installation** | `src/axora/cli.py`, `src/axora/setup/mysql_install.py` | Affichage terminal en direct des étapes de traitement, d'introspection et d'installation MySQL avec statuts `[*]` et `[!]`. |
| **Suite de tests** | `tests/test_progress.py`, `tests/test_agent_loop.py` | Validation complète des 9 critères d'acceptation (ordre, sécurité, absence de fuite d'arguments, streaming, concurrence, erreurs). |

---

**Axora — From intent to action.**
