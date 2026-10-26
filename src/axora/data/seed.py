import asyncio
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from axora.data.database import AsyncSessionLocal
from axora.data.dynamic_models import build_dynamic_tables
from axora.data.mutation_engine import MutationEngine
from axora.semantic.service import SemanticModelService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("axora.seed")

YAML_PATH = Path("src/axora/semantic/definitions/gestion_paroissiale.yaml")


async def seed_database(session: AsyncSession | None = None) -> dict[str, list[dict]]:
    """Seeds the database with initial realistic test dataset according to the semantic model manifest."""
    logger.info("Initializing semantic model service for seeding...")
    semantic_service = SemanticModelService.from_yaml(YAML_PATH)
    build_dynamic_tables(semantic_service)

    mutation_engine = MutationEngine(semantic_service)
    close_session = False

    if session is None:
        session = AsyncSessionLocal()
        close_session = True

    try:
        async with session.begin():
            logger.info("Seeding Paroisses...")
            p1 = await mutation_engine.create_record(session, "Paroisse", {"nom": "Andranovelona"})
            p2 = await mutation_engine.create_record(session, "Paroisse", {"nom": "Analamanga"})

            logger.info("Seeding Zones Géographiques...")
            z1_1 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p1["id"], "nom": "Andoharanofotsy"})
            z1_2 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p1["id"], "nom": "Anfarihy"})
            z2_1 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p2["id"], "nom": "Centre-Ville"})
            z2_2 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p2["id"], "nom": "Nord-Analamanga"})

            logger.info("Seeding Associations Standard...")
            assocs = []
            for p in (p1, p2):
                a_h = await mutation_engine.create_record(session, "Association", {"paroisse_id": p["id"], "nom": "Association des Hommes", "code": "HOMMES"})
                a_f = await mutation_engine.create_record(session, "Association", {"paroisse_id": p["id"], "nom": "Association des Femmes", "code": "FEMMES"})
                a_j = await mutation_engine.create_record(session, "Association", {"paroisse_id": p["id"], "nom": "Association des Jeunes", "code": "JEUNES"})
                a_s = await mutation_engine.create_record(session, "Association", {"paroisse_id": p["id"], "nom": "École du Sabbat", "code": "ECOLE_SABBAT"})

                # Ensure paroisse_id is preserved in returned association metadata dict
                a_h["paroisse_id"] = p["id"]
                a_f["paroisse_id"] = p["id"]
                a_j["paroisse_id"] = p["id"]
                a_s["paroisse_id"] = p["id"]
                assocs.extend([a_h, a_f, a_j, a_s])

            logger.info("Seeding Membres...")
            m1 = await mutation_engine.create_record(session, "Membre", {
                "paroisse_id": p1["id"],
                "zone_geographique_id": z1_1["id"],
                "nom": "Rakoto",
                "prenom": "Jean",
                "adresse": "Lot II B 12 Andoharanofotsy",
                "sexe": "HOMME",
                "date_naissance": "1992-04-15",
                "statut_matrimonial": "CELIBATAIRE",
            })

            m2 = await mutation_engine.create_record(session, "Membre", {
                "paroisse_id": p1["id"],
                "zone_geographique_id": z1_1["id"],
                "nom": "Rasoa",
                "prenom": "Marie",
                "adresse": "Lot IV K 45 Andoharanofotsy",
                "sexe": "FEMME",
                "date_naissance": "1995-08-20",
                "statut_matrimonial": "CELIBATAIRE",
            })

            m3 = await mutation_engine.create_record(session, "Membre", {
                "paroisse_id": p1["id"],
                "zone_geographique_id": z1_2["id"],
                "nom": "Randria",
                "prenom": "Paul",
                "adresse": "Lot I A 08 Anfarihy",
                "sexe": "HOMME",
                "date_naissance": "1980-02-10",
                "statut_matrimonial": "MARIE",
            })

            m4 = await mutation_engine.create_record(session, "Membre", {
                "paroisse_id": p2["id"],
                "zone_geographique_id": z2_1["id"],
                "nom": "Rabe",
                "prenom": "Michel",
                "adresse": "Rue de l'Indépendance Centre-Ville",
                "sexe": "HOMME",
                "date_naissance": "2012-06-01",
                "statut_matrimonial": "CELIBATAIRE",
            })

            logger.info("Seeding Adhésions aux Associations...")
            a_j1 = next(a for a in assocs if a["paroisse_id"] == p1["id"] and a["code"] == "JEUNES")
            a_h1 = next(a for a in assocs if a["paroisse_id"] == p1["id"] and a["code"] == "HOMMES")
            a_s2 = next(a for a in assocs if a["paroisse_id"] == p2["id"] and a["code"] == "ECOLE_SABBAT")

            adh1 = await mutation_engine.create_record(session, "AdhesionAssociation", {
                "membre_id": m1["id"],
                "association_id": a_j1["id"],
                "date_adhesion": "2020-01-01",
            })
            adh2 = await mutation_engine.create_record(session, "AdhesionAssociation", {
                "membre_id": m3["id"],
                "association_id": a_h1["id"],
                "date_adhesion": "2015-05-12",
            })
            adh3 = await mutation_engine.create_record(session, "AdhesionAssociation", {
                "membre_id": m4["id"],
                "association_id": a_s2["id"],
                "date_adhesion": "2021-09-01",
            })

            logger.info("Seeding Demandes de Passage...")
            dp1 = await mutation_engine.create_record(session, "DemandePassage", {
                "membre_id": m1["id"],
                "paroisse_origine_id": p1["id"],
                "paroisse_destination_id": p2["id"],
                "date_demande": "2024-03-01",
                "date_debut_passage": "2024-04-01",
                "date_fin_passage": "2024-04-30",
                "statut": "APPROUVEE",
            })

            logger.info("Seeding Historique des Rattachements...")
            hr1 = await mutation_engine.create_record(session, "HistoriqueRattachement", {
                "membre_id": m1["id"],
                "nouvelle_paroisse_id": p1["id"],
                "nouvelle_zone_id": z1_1["id"],
                "date_effet": "2020-01-01",
            })

            logger.info("Seeding de la base de données terminé avec succès !")

            return {
                "paroisses": [p1, p2],
                "zones": [z1_1, z1_2, z2_1, z2_2],
                "associations": assocs,
                "membres": [m1, m2, m3, m4],
                "adhesions": [adh1, adh2, adh3],
                "demandes_passage": [dp1],
                "historiques": [hr1],
            }
    finally:
        if close_session:
            await session.close()


def main():
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()
