# Axora — Seeding Automatique de la Base de Données pour Tests

**Version :** 1.2
**Statut :** Documentation technique du module de seeding automatique
**Composants :** `src/axora/data/seed.py`, `tests/test_seed.py`

---

## 1. Présentation du Seeding

Le module `src/axora/data/seed.py` permet d alimenter automatiquement la base de données PostgreSQL (ou SQLite en-mémoire pour les tests) avec un jeu de données de test réaliste conforme au modèle sémantique de la gestion paroissiale.

---

## 2. Jeu de Données Inséré (`Dataset`)

Le script de seeding génère les enregistrements suivants :

| Entité | Quantité Insérée | Détails & Exemples |
|---|---|---|
| **Paroisse** | 2 | `Andranovelona`, `Analamanga` |
| **ZoneGeographique** | 4 | `Andoharanofotsy`, `Anfarihy`, `Centre-Ville`, `Nord-Analamanga` |
| **Association** | 8 | 4 associations standard (`HOMMES`, `FEMMES`, `JEUNES`, `ECOLE_SABBAT`) par paroisse |
| **Membre** | 4 | Exemples: `Rakoto Jean` (Homme, Céliabtaire), `Rasoa Marie` (Femme, Célibataire), `Randria Paul` (Marié), `Rabe Michel` (Enfant < 16 ans) |
| **AdhesionAssociation** | 3 | Adhésion de Jean à l Association des Jeunes, de Paul à l Association des Hommes, de Michel à l École du Sabbat |
| **DemandePassage** | 1 | Demande temporaire de passage approuvée pour Jean de Andranovelona vers Analamanga |
| **HistoriqueRattachement**| 1 | Historique d affectation initiale de Jean à la zone Andoharanofotsy |

---

## 3. Lancement du Seeding

### En local (Sans Docker) :
```bash
PYTHONPATH=src python3 -m axora.data.seed
```

### Via Docker Compose :
```bash
docker compose exec api python -m axora.data.seed
```

---

## 4. Validation par les Tests Automatiques

La suite de tests unitaires et d intégration dans `tests/test_seed.py` vérifie :
1. Le comptage exact des enregistrements créés par entité.
2. L exécution de requêtes relationnelles complexes sur les membres d une zone/paroisse spécifique.

**Commande d exécution :**
```bash
PYTHONPATH=src python3 -m pytest tests/test_seed.py
```

---

**Axora — From intent to action.**
