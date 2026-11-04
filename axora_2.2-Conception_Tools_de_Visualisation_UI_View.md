# AXORA — Conception Technique : Outils de Visualisation Dynamique & Generative UI (View Tools)

> **Document de Conception Fonctionnelle et Technique (Spécification v2.2)**
> *Présentation enrichie des résultats de l'agent : Grilles/Tableaux interactifs, Graphiques statistiques, Cartes KPI & Graphes relationnels.*

---

## 💡 1. Compréhension du Besoin Métier

### Le Constat Actuel
Actuellement, lorsque l'Agent Axora traite une intention utilisateur (ex: *"Lister les membres"*, *"Statistique des membres par paroisse"*, *"Répartition des âges"*), la réponse finale est renvoyée sous forme de **texte Markdown brut** ou de tableau Markdown statique.
Bien que lisible, ce format présente des limites majeures pour l'utilisateur final :
1. **Pas d'interactivité** : Impossible de trier dynamiquement les colonnes, de filtrer localement, de paginer ou d'exporter facilement.
2. **Faible impact visuel pour les statistiques** : Une liste textuelle comme `Andranovelona: 2, Analamanga: 2` est beaucoup moins percutante qu'un graphique en barres ou un diagramme circulaire (Pie Chart).
3. **Absence de hiérarchie visuelle pour les métriques clés** : Un nombre total ou un taux d'adhésion devrait être affiché sous forme de **Cartes Métriques / KPI** immédiatement lisibles.

### La Solution : Architecture "Generative UI" & "View Tools"
L'Agent Axora ne doit pas seulement être capable de faire du *Query* ou de la *Mutation* de données, il doit être capable de **décider de la meilleure forme de restitution visuelle** pour l'utilisateur en appelant des **Outils de Visualisation (View Tools)**.

```text
[Intention Utilisateur]
         │
         ▼
[Runtime Agent Axora]
         │
         ├─── 1. Query Tool: Récupère les données (`query_data`)
         │
         └─── 2. View Tool: Sélectionne le composant visuel adapté :
                  ├── `render_table`       (Grille dense, tri, recherche, export)
                  ├── `render_chart`       (Barres, Camembert, Courbes, Donut)
                  ├── `render_metric_card` (KPIs, Compteurs, Résumés exécutifs)
                  └── `render_graph`       (Réseaux de relations, organigrammes)
```

---

## 🧱 2. Catalogue des Outils de Visualisation Proposés

### 2.1 Outil `render_table` (Data Grid & Tableaux Riches)
- **Rôle** : Restituer des listes d'entités avec pagination, recherche locale, tri par colonne et actions contextuelles.
- **Paramètres Schéma JSON** :
  ```json
  {
    "title": "Liste des Membres",
    "description": "4 membres enregistrés",
    "columns": [
      {"key": "nom", "label": "Nom de famille", "type": "string", "sortable": true},
      {"key": "prenom", "label": "Prénom", "type": "string", "sortable": true},
      {"key": "statut_matrimonial", "label": "Statut", "type": "badge"},
      {"key": "paroisse", "label": "Paroisse", "type": "string"},
      {"key": "associations", "label": "Associations", "type": "tags"}
    ],
    "rows": [
      {"nom": "Rakoto", "prenom": "Jean", "statut_matrimonial": "CELIBATAIRE", "paroisse": "Andranovelona", "associations": ["Association des Jeunes"]},
      {"nom": "Rasoa", "prenom": "Marie", "statut_matrimonial": "CELIBATAIRE", "paroisse": "Andranovelona", "associations": []}
    ],
    "actions": ["export_csv", "export_pdf", "filter"]
  }
  ```

---

### 2.2 Outil `render_chart` (Graphiques Statistiques)
- **Rôle** : Afficher des visualisations analytiques pour répondre à des questions quantitatives ou comparatives.
- **Types de Graphiques Supportés** :
  - `bar` : Répartitions comparatives (ex: Membres par paroisse, Membres par association).
  - `donut` / `pie` : Proportions (ex: Répartition Homme / Femme, Statut célibataire vs marié).
  - `line` : Évolutions temporelles (ex: Évolution des adhésions ou passages par mois).
- **Paramètres Schéma JSON** :
  ```json
  {
    "chart_type": "bar",
    "title": "Répartition des Membres par Paroisse",
    "x_axis_label": "Paroisse",
    "y_axis_label": "Nombre de membres",
    "data": [
      {"label": "Andranovelona", "value": 2, "color": "#1d4ed8"},
      {"label": "Analamanga", "value": 2, "color": "#0284c7"}
    ]
  }
  ```

---

### 2.3 Outil `render_metric_card` (Cartes KPI & Synthèses)
- **Rôle** : Mettre en valeur des chiffres clés immédiats (Total membres, Moyenne d'âge, Nouveaux arrivants).
- **Paramètres Schéma JSON** :
  ```json
  {
    "cards": [
      {
        "title": "Total des Membres",
        "value": "4",
        "trend": "+2 ce mois",
        "trend_type": "positive",
        "icon": "users"
      },
      {
        "title": "Paroisses Actives",
        "value": "2",
        "trend": "100% opérationnelles",
        "trend_type": "neutral",
        "icon": "church"
      },
      {
        "title": "Membres Sans Association",
        "value": "1",
        "trend": "Rasoa Marie",
        "trend_type": "warning",
        "icon": "alert-circle"
      }
    ]
  }
  ```

---

### 2.4 Outil `render_network_graph` (Graphe Sémantique & Liens Relationnels)
- **Rôle** : Représenter visuellement les liens entre entités (Ex: Paroisse → Zones → Membres → Associations).
- **Technologie Web** : React Flow / Vis.js.

---

## 🔄 3. Intégration dans le Cycle de Décision de l'Agent

Comment l'Agent choisit-il le View Tool approprié ?

1. **Cas 1 : Question d'identification individuelle** (Ex: *"Qui est Rasoa ?"*)
   -> L'Agent privilégie une **Fiche Profil** (`render_metric_card` ou texte explicatif riche).

2. **Cas 2 : Question d'inventaire ou de liste** (Ex: *"Lister les membres", "Quels membres n'ont pas d'association ?"*)
   -> L'Agent appelle `query_data` puis transmet le jeu de données à `render_table` avec les colonnes et badges adéquats.

3. **Cas 3 : Question de statistique ou de répartition** (Ex: *"Donne-moi les statistiques de membres par église"*)
   -> L'Agent agrège les données et génère un appel `render_chart` (Bar/Donut) accompagné d'un court commentaire d'analyse.

---

## 🎨 4. Composants Front-End de Rendu (Next.js / React)

Dans l'application Web (`web/src/components/views/`) :
- `TableView.tsx` : Rendu du tableau avec Tailwind CSS, tri (`useState`), recherche instantanée et export CSV.
- `ChartView.tsx` : Composant basé sur Recharts ou Chart.js / SVG pur ultra-léger.
- `MetricCardView.tsx` : Grille de tuiles KPI avec badges d'alerte et icônes Lucide.
- `ViewDispatcher.tsx` : Composant qui inspecte la réponse de l'agent et monte automatiquement le bon visualiseur.

---

## 📋 5. Plan d'Implémentation Recommandé

1. **Phase 1 (Backend)** :
   - Déclaration des interfaces et schémas JSON des View Tools (`render_table`, `render_chart`, `render_metric_card`) dans `src/axora/tools/views/`.
   - Intégration dans le registre `ToolRegistry`.
2. **Phase 2 (Frontend)** :
   - Création des composants de rendu React correspondants dans `web/src/components/views/`.
   - Support du rendu interactif dans `ChatCanvas.tsx`.
3. **Phase 3 (Validation & Tests)** :
   - Tests de non-régression et démonstration sur les requêtes statistiques paroissiales.

---

*Document de conception établi pour la validation et l'implémentation des View Tools Axora.*
