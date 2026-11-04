# AXORA — Implémentation : Architecture Extensible des Outils de Vue (View Tools)

> **Guide d'Implémentation et d'Extension (Backend Python & Frontend Next.js / React)**
> *Comment injecter et ajouter de nouveaux types de vues (cartes, graphiques, diagrammes, heatmaps, kanban) sans modifier le coeur d'Axora.*

---

## 🎯 1. Vue d'Ensemble de l'Architecture Injectable

L'architecture des vues d'Axora repose sur le **Design Pattern Registry** symétrique entre le backend et le frontend :

```text
Backend (Python)                             Frontend (Next.js / React)
────────────────────────                     ──────────────────────────
ViewBuilderInterface ───────────────►        ViewPayload Contract (JSON)
       │                                                 │
       ▼                                                 ▼
ViewRegistry (Injectable)                    ViewDispatcher (Extensible)
├── DynamicTableViewBuilder                  ├── TableView (Sorting, Search, CSV)
├── DynamicChartViewBuilder                  ├── ChartView (SVG Bar & Donut)
├── DynamicMetricCardsBuilder                ├── MetricCardView (KPIs)
└── [Votre Nouveau Builder]                  └── [Votre Nouveau Composant]
```

---

## 🐍 2. Côté Backend : Comment Créer et Injecter une Nouvelle Vue

### Étape 1 : Implémenter l'interface `ViewBuilderInterface`
Créez votre classe en héritant de `ViewBuilderInterface` dans `src/axora/views/builders.py` (ou dans votre module applicatif) :

```python
from typing import Any
from axora.views.interface import ViewBuilderInterface, ViewPayload


class KanbanViewBuilder(ViewBuilderInterface):
    """Exemple : Builder pour un tableau de progression Kanban."""

    @property
    def view_type(self) -> str:
        return "kanban"

    def build(self, data: Any, title: str = "Kanban", **kwargs: Any) -> ViewPayload:
        # Transformation dynamique de vos données
        columns = data.get("columns", ["À faire", "En cours", "Terminé"])
        cards = data.get("cards", [])

        return ViewPayload(
            view_type="kanban",
            title=title,
            data={
                "columns": columns,
                "cards": cards,
            },
        )
```

### Étape 2 : Injecter le Builder dans le `ViewRegistry`
Dans `src/axora/api/routes.py` (ou lors du bootstrap de votre runtime) :

```python
from axora.views.registry import ViewRegistry

view_registry = ViewRegistry()
# Enregistrement des builders standards
view_registry.register(DynamicTableViewBuilder(semantic_service))
view_registry.register(DynamicChartViewBuilder())
view_registry.register(DynamicMetricCardsBuilder())

# Injection de votre nouveau builder
view_registry.register(KanbanViewBuilder())
```

---

## ⚛️ 3. Côté Frontend : Comment Déclarer le Composant de Vue

### Étape 1 : Créer le Composant React
Dans `web/src/components/views/KanbanView.tsx` :

```tsx
'use client'

import React from 'react'

interface KanbanViewProps {
  title?: string
  data: {
    columns: string[]
    cards: Array<{ id: string; title: string; column: string }>
  }
}

export const KanbanView: React.FC<KanbanViewProps> = ({ title, data }) => {
  return (
    <div className="border border-slate-200 rounded-xl p-4 bg-white mt-3">
      <h4 className="text-xs font-bold text-slate-900 mb-3">{title}</h4>
      <div className="grid grid-cols-3 gap-3">
        {data.columns.map((col) => (
          <div key={col} className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
            <span className="text-[11px] font-semibold text-slate-700">{col}</span>
            <div className="mt-2 space-y-1.5">
              {data.cards.filter(c => c.column === col).map(c => (
                <div key={c.id} className="p-2 bg-white rounded border text-xs shadow-2xs">
                  {c.title}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

### Étape 2 : Enregistrer le Composant dans `ViewDispatcher.tsx`
Dans `web/src/components/views/ViewDispatcher.tsx` :

```tsx
import { KanbanView } from './KanbanView'
import { registerCustomView } from './ViewDispatcher'

// Enregistrement immédiat ou à chaud
registerCustomView('kanban', KanbanView)
```

---

## 🔄 4. Fonctionnement Automatique pour les Requêtes Sémantiques

Lorsque l'Agent exécute `query_data` :
1. Les enregistrements enrichis de leurs relations (`paroisse`, `associations`, etc.) sont transmis à `DynamicTableViewBuilder`.
2. Le `DynamicTableViewBuilder` analyse dynamiquement les clés du dictionnaire :
   - Les listes (ex: `associations`) reçoivent le type `tags`.
   - Les champs énumérés à valeurs restreintes (`statut_matrimonial`, `sexe`) reçoivent le type `badge`.
   - Les dates reçoivent le type `date`.
   - Les chiffres reçoivent le type `number`.
3. L'API renvoie le `ViewPayload` dans le JSON de réponse `/api/v1/chat` (`view`).
4. Le frontend monte automatiquement le bon composant interactif.

---

*Documentation technique d'extensibilité des vues validée pour Axora v2.3.*


---

## 📊 5. Les 4 Types de Visualisations Dynamiques Implémentées

### 5.1 Graphique en Barres (`view_type: "chart"`, `chart_type: "bar"`)
- **Usage** : Comparaisons quantitatives (ex: répartition des membres par église, effectifs par association).
- **Rendu Frontend** : Jauges horizontales interactives avec calcul automatique des pourcentages et mise en valeur des maximums.
- **Payload Dynamique Exemple** :
  ```json
  {
    "view_type": "chart",
    "title": "Répartition par Entité",
    "data": {
      "chart_type": "bar",
      "series": [
        {"label": "Andranovelona", "value": 2, "color": "#1d4ed8"},
        {"label": "Analamanga", "value": 2, "color": "#0284c7"}
      ],
      "total": 4
    }
  }
  ```

---

### 5.2 Camembert / Pie (`view_type: "chart"`, `chart_type: "pie"` ou `"donut"`)
- **Usage** : Proportions et pourcentages d'un ensemble (ex: répartition par sexe, proportions de statut matrimonial).
- **Rendu Frontend** : Secteurs SVG trigonométriques fluides ou Donut central avec légende et pourcentages arrondis.
- **Payload Dynamique Exemple** :
  ```json
  {
    "view_type": "chart",
    "title": "Répartition par Statut",
    "data": {
      "chart_type": "donut",
      "series": [
        {"label": "Célibataire", "value": 3, "color": "#1d4ed8"},
        {"label": "Marié", "value": 1, "color": "#10b981"}
      ],
      "total": 4
    }
  }
  ```

---

### 5.3 Courbe Temporelle (`view_type: "chart"`, `chart_type: "line"`)
- **Usage** : Évolutions chronologiques (ex: historique d'adhésions par année, demandes de transfert par mois).
- **Rendu Frontend** : Courbe SVG lissée avec points d'ancrage, étiquettes de temps sur l'axe X, et dégradé translucide sous la courbe.
- **Payload Dynamique Exemple** :
  ```json
  {
    "view_type": "chart",
    "title": "Évolution Chronologique",
    "data": {
      "chart_type": "line",
      "x_label": "Année / Période",
      "y_label": "Nombre d'enregistrements",
      "series": [
        {"label": "2020", "value": 1},
        {"label": "2021", "value": 3},
        {"label": "2022", "value": 4}
      ]
    }
  }
  ```

---

### 5.4 Indicateurs Clés KPI (`view_type: "metric_cards"`)
- **Usage** : Synthèses exécutives immédiates de haut niveau.
- **Rendu Frontend** : Grille de cartes avec chiffres en grand caractère, flèches de tendance (hausse/baisse), badges d'état (`success`, `warning`, `danger`, `neutral`).
- **Payload Dynamique Exemple** :
  ```json
  {
    "view_type": "metric_cards",
    "title": "Indicateurs Métier",
    "data": {
      "cards": [
        {"label": "Total Enregistrements", "value": "4", "trend": "+2 ce mois", "status": "success"},
        {"label": "Paroisses Actives", "value": "2", "status": "neutral"},
        {"label": "Sans Rattachement", "value": "1", "trend": "À régulariser", "status": "warning"}
      ]
    }
  }
  ```

---

## 🛡️ 6. Garantie Zéro Code Figé (Dynamisme Absolu)

Pour respecter la consigne d'éviter tout code figé (noms de tables ou colonnes) :
1. **Extraction par introspection** : `DynamicChartViewBuilder` et `DynamicMetricCardsBuilder` n'ont aucune clé pré-codée. Ils parcourent les dictionnaires reçus et détectent automatiquement la clé descriptive (ex: `label`, `name`, `date`, `titre`) et la clé numérique (ex: `value`, `count`, `total`).
2. **Détection du format de colonne** : `DynamicTableViewBuilder` interroge le `SemanticModelService` pour savoir si un champ est une relation (tags), un enum (badge), une date ou un nombre sans mentionner explicitement de nom de table ou de colonne.
