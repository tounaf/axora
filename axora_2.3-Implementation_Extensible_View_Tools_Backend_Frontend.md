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
