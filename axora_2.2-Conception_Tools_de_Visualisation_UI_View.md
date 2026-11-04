# AXORA — Conception Technique : Outils de Visualisation Dynamique & Generative UI (View Tools)

> **Document de Conception Fonctionnelle et Technique (Spécification v2.2 - 100% Dynamique & Agnostique du Domaine)**
> *Principe directeur : Aucune table, aucune colonne ni entité n'est figée en dur dans le code ou les schémas. Tout est dérivé à la volée du Modèle Sémantique et du schéma de données actif.*

---

## 💡 1. Compréhension du Besoin & Principes Architecturaux

### 1.1 Objectif
Permettre à l'Agent Axora de restituer les données métier sous forme de composants interactifs riches (**Tableaux interactifs / Data Grids**, **Graphiques statistiques**, **Cartes KPI**) plutôt qu'en simple texte brut ou Markdown statique, **SANS JAMAIS figer de noms de tables ni de colonnes** dans le code.

### 1.2 Règle d'Or : Génération Sémantique 100% Dynamique
Pour préserver la portabilité totale d'Axora sur n'importe quel domaine métier (qu'il s'agisse de gestion paroissiale, de vente de marchandises PPN, de cabinet juridique ou de logistique) :
1. **Zéro constante codée en dur** : Ni nom d'entité, ni nom de colonne, ni nom de table n'apparaît dans les signatures ou les types de code.
2. **Dérivation automatique via `SemanticModelService`** :
   - Les types d'affichage de colonnes (`badge`, `tag`, `date`, `number`, `text`) sont déduits automatiquement des types d'attributs du manifeste (`attribute_def.type`, `attribute_def.allowed_values`).
   - Les colonnes relationnelles (1-N, N-N) sont détectées à partir de `entity_def.relationships` et formatées dynamiquement.
3. **Schéma Universel d'Échange Agent ⇄ UI** : L'Agent renvoie une charge utile générique que le frontend React/Next.js sait interpréter sans connaître le modèle sous-jacent.

```text
[Modèle Sémantique Actif (YAML/DB)]
              │
              ▼
    [Agent Decision Loop]
              │
    ┌─────────┴─────────────────────────────┐
    ▼                                       ▼
`query_data` (Extraction brute)      `View Builder` (Génération dynamique du View Contract)
    │                                       │
    └──────────────────┬────────────────────┘
                       ▼
       [Contrat Visuel Universel JSON]
       (columns, rows, chart_type, series)
                       │
                       ▼
       [Next.js Dynamic View Dispatcher]
       ├── `TableView` (Tri, recherche, export)
       ├── `ChartView` (Bar, Pie, Donut, Line)
       └── `MetricCardView` (KPIs)
```

---

## 📐 2. Schémas Universels des Outils de Visualisation (View Contracts)

Les outils de visualisation ne manipulent que des structures abstraites et auto-descriptives.

### 2.1 Contrat Universel `render_table` (Grille de Données Dynamique)

L'outil `render_table` ne fige aucune colonne ; les métadonnées de chaque colonne sont générées dynamiquement à partir des attributs inspectés dans le modèle sémantique.

#### Schéma d'Appel de l'Outil (Tool Signature)
```json
{
  "name": "render_table",
  "description": "Restitue un ensemble d'enregistrements sous forme de tableau interactif dynamique avec tri, recherche et export.",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Titre du tableau adapté au contexte"
      },
      "entity": {
        "type": "string",
        "description": "Nom de l'entité canonique concernée (découverte dynamiquement)"
      },
      "columns": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "key": {"type": "string", "description": "Clé technique de l'attribut"},
            "label": {"type": "string", "description": "Libellé lisible généré d'après la description sémantique"},
            "data_type": {
              "type": "string",
              "enum": ["string", "number", "date", "badge", "tags", "boolean"]
            },
            "sortable": {"type": "boolean", "default": true}
          },
          "required": ["key", "label", "data_type"]
        }
      },
      "rows": {
        "type": "array",
        "items": {"type": "object"},
        "description": "Liste d'objets clé-valeur correspondant aux colonnes déclarées"
      },
      "summary_text": {
        "type": "string",
        "description": "Texte de synthèse explicatif accompagnant la grille"
      }
    },
    "required": ["title", "columns", "rows"]
  }
}
```

#### Déduction Automatique du `data_type` par le Backend
À l'exécution, le moteur inspecte l'attribut dans `entity_def.attributes` :
- Si `attr_def.allowed_values` existe (ex: enum statut, rôles) -> `data_type = "badge"`.
- Si l'attribut est une relation `many-to-many` ou `one-to-many` retournant une liste -> `data_type = "tags"`.
- Si `attr_def.type == "date"` -> `data_type = "date"` (avec formatage localisé automatique `DD/MM/YYYY`).
- Si `attr_def.type in ("integer", "float", "number")` -> `data_type = "number"` (alignement à droite).
- Sinon -> `data_type = "string"`.

---

### 2.2 Contrat Universel `render_chart` (Graphiques Statistiques Agnostiques)

Aucun axe ni série n'est figé. Que l'utilisateur demande une statistique par région, par statut, par église ou par produit, le schéma reste strictement le même.

#### Schéma d'Appel de l'Outil (Tool Signature)
```json
{
  "name": "render_chart",
  "description": "Génère un graphique statistique interactif (barres, camembert, lignes) à partir de données catégorielles ou chronologiques.",
  "parameters": {
    "type": "object",
    "properties": {
      "chart_type": {
        "type": "string",
        "enum": ["bar", "donut", "pie", "line"]
      },
      "title": {
        "type": "string",
        "description": "Titre explicite du graphique"
      },
      "category_key": {
        "type": "string",
        "description": "Nom du champ d'axe ou de catégorie"
      },
      "metric_key": {
        "type": "string",
        "description": "Nom du champ de mesure ou valeur"
      },
      "series": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "label": {"type": "string", "description": "Libellé de la catégorie"},
            "value": {"type": "number", "description": "Valeur numérique calculée"},
            "color": {"type": "string", "description": "Code couleur hex optionnel"}
          },
          "required": ["label", "value"]
        }
      },
      "analysis_text": {
        "type": "string",
        "description": "Commentaire d'analyse métier produit par l'agent"
      }
    },
    "required": ["chart_type", "title", "series"]
  }
}
```

---

### 2.3 Contrat Universel `render_metric_cards` (Tuiles KPIs Dynamiques)

Permet d'afficher des indicateurs de haut niveau calculés dynamiquement.

#### Schéma d'Appel de l'Outil (Tool Signature)
```json
{
  "name": "render_metric_cards",
  "description": "Affiche un ensemble de cartes métriques pour des synthèses numériques clés.",
  "parameters": {
    "type": "object",
    "properties": {
      "cards": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "label": {"type": "string", "description": "Titre du KPI"},
            "value": {"type": "string", "description": "Valeur principale formatée"},
            "description": {"type": "string", "description": "Sous-titre ou contexte"},
            "status": {
              "type": "string",
              "enum": ["neutral", "success", "warning", "danger"]
            }
          },
          "required": ["label", "value"]
        }
      }
    },
    "required": ["cards"]
  }
}
```

---

## ⚙️ 3. Mécanisme de Construction Dynamique Côté Backend

Pour éviter tout couplage fort avec les entités dans le code Python :

### 3.1 Service Générateur `DynamicViewBuilder`
Un nouveau service `DynamicViewBuilder` reçoit les enregistrements bruts retournés par `QueryEngine` ainsi que la définition de l'entité (`EntityDefinition`) :

```python
class DynamicViewBuilder:
    def __init__(self, semantic_service: SemanticModelService):
        self._semantic = semantic_service

    def build_table_payload(self, entity_name: str, records: list[dict[str, Any]], title: str | None = None) -> dict[str, Any]:
        entity_def = self._semantic.get_entity_details(entity_name)
        if not entity_def or not records:
            return {"title": title or entity_name, "columns": [], "rows": records}

        # Découverte dynamique des colonnes présentes dans les données
        sample_keys = list(records[0].keys())
        columns = []

        for key in sample_keys:
            if key in ("id", f"{entity_def.storage.table}_id"):
                continue

            attr_def = entity_def.attributes.get(key)
            rel_def = entity_def.relationships.get(key)

            # Déduction dynamique du type d'affichage
            if attr_def and attr_def.allowed_values:
                data_type = "badge"
                label = attr_def.description or key.capitalize().replace("_", " ")
            elif isinstance(records[0].get(key), list):
                data_type = "tags"
                label = key.capitalize().replace("_", " ")
            elif attr_def and attr_def.type == "date":
                data_type = "date"
                label = attr_def.description or key.capitalize().replace("_", " ")
            elif isinstance(records[0].get(key), (int, float)):
                data_type = "number"
                label = key.capitalize().replace("_", " ")
            else:
                data_type = "string"
                label = (attr_def.description if attr_def else key).capitalize().replace("_", " ")

            columns.append({
                "key": key,
                "label": label,
                "data_type": data_type,
                "sortable": True
            })

        return {
            "title": title or f"Liste des {entity_name}s",
            "entity": entity_name,
            "columns": columns,
            "rows": records,
        }
```

---

## 🖥️ 4. Rendu Front-End Next.js / React (`web/`)

Dans le frontend Next.js :
1. Le composant `ChatCanvas.tsx` reçoit la réponse de l'API.
2. Si le payload contient un bloc `ui_view`:
   - `view_type == "table"` -> Monte le composant `DynamicTableView`.
   - `view_type == "chart"` -> Monte le composant `DynamicChartView`.
   - `view_type == "metric_cards"` -> Monte `DynamicMetricCardsView`.
3. Les composants React sont **100% génériques** :
   - `DynamicTableView` génère les `<th>` en bouclant sur `columns` et les `<td>` en bouclant sur `rows[col.key]`.
   - Les badges (`badge`) affichent une puce colorée basée sur la valeur textuelle sans connaître d'avance les libellés possibles.
   - Les tags (`tags`) effectuent un simple `map` sur la liste des chaînes de caractères.
   - `DynamicChartView` lit les champs universels `label` et `value` de `series`.

---

## 🚀 5. Bénéfices Immédiats

1. **Flexibilité Absolue** : Vous pouvez modifier, ajouter ou supprimer des entités et attributs dans `gestion_paroissiale.yaml` ; l'interface s'adaptera instantanément sans aucune modification de code.
2. **Support de Nouveaux Domaines** : Charger un modèle de gestion de stocks PPN ou de facturation produit immédiatement des tableaux et graphiques parfaits.
3. **Expérience Utilisateur Moderne** : Finis les blocs de texte Markdown monotones ; l'utilisateur bénéficie d'une véritable interface applicative vivante et réactive.

---

*Spécification technique de conception validée pour le développement des View Tools Axora.*
