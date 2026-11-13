import asyncio
import datetime
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

# Diverse Malagasy family names and given names for scalable realistic dataset
FAMILY_NAMES = [
    "Rakoto", "Rasoa", "Randria", "Rabe", "Harinjatovo", "Ramanana", "Rasolofo",
    "Razafy", "Rajaona", "Andriana", "Rakotomalala", "Randrianarisoa", "Ravalomanana",
    "Ratsiraka", "Rabemananjara", "Rafalimanana", "Razafindrakoto", "Andriantsitohaina",
    "Razanamparany", "Ramaroson", "Rakotondrabe", "Randriamanantena", "Rasamoelina",
    "Ratsimbazafy", "Rakotoniaina", "Ranaivo", "Razafindrabe", "Rakotondrasoa",
    "Randrianasolo", "Rabenjamina",
]

FIRST_NAMES_MALE = [
    "Jean", "Paul", "Michel", "Fetra", "Samuel", "David", "Daniel", "Thomas",
    "Hery", "Mamy", "Eric", "Andry", "Thierry", "Nicolas", "Olivier", "Luc",
    "Patrick", "Julien", "Alain", "Christian", "Stéphane", "Benoit", "Gabriel",
]

FIRST_NAMES_FEMALE = [
    "Marie", "Léa", "Sarah", "Esther", "Ruth", "Voahirana", "Bakoly", "Faniry",
    "Mirana", "Soa", "Hasina", "Holy", "Lova", "Nirina", "Aina", "Haingo",
    "Mialy", "Tantely", "Rova", "Fara", "Onja", "Santatra", "Eliane",
]

DISTRICTS = [
    "Andoharanofotsy", "Anfarihy", "Centre-Ville", "Nord-Analamanga", "Tanjombato",
    "Itaosy", "Sabotsy-Namehana", "Ambohimangakely", "Ankorondrano", "Analakely",
    "Mahamasina", "Ambohipo", "Ankatso", "Isoraka", "Antanimena",
]


async def seed_database(session: AsyncSession | None = None, target_member_count: int = 100) -> dict[str, list[dict]]:
    """Seeds the database with an extensive, realistic dataset of 100+ members and associated relations."""
    logger.info("Initializing semantic model service for scalable seeding...")
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
            p3 = await mutation_engine.create_record(session, "Paroisse", {"nom": "Atsimondrano"})
            p4 = await mutation_engine.create_record(session, "Paroisse", {"nom": "Avaradrano"})
            paroisses = [p1, p2, p3, p4]

            logger.info("Seeding Zones Géographiques...")
            zones = []
            z1_1 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p1["id"], "nom": "Andoharanofotsy"})
            z1_2 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p1["id"], "nom": "Anfarihy"})
            z2_1 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p2["id"], "nom": "Centre-Ville"})
            z2_2 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p2["id"], "nom": "Nord-Analamanga"})
            z3_1 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p3["id"], "nom": "Tanjombato"})
            z3_2 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p3["id"], "nom": "Itaosy"})
            z4_1 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p4["id"], "nom": "Sabotsy-Namehana"})
            z4_2 = await mutation_engine.create_record(session, "ZoneGeographique", {"paroisse_id": p4["id"], "nom": "Ambohimangakely"})
            zones.extend([z1_1, z1_2, z2_1, z2_2, z3_1, z3_2, z4_1, z4_2])

            parish_zones_map = {
                p1["id"]: [z1_1, z1_2],
                p2["id"]: [z2_1, z2_2],
                p3["id"]: [z3_1, z3_2],
                p4["id"]: [z4_1, z4_2],
            }

            logger.info("Seeding Standard Associations per Paroisse...")
            assocs = []
            parish_assoc_map = {}
            for p in paroisses:
                a_h = await mutation_engine.create_record(session, "Association", {"paroisse_id": p["id"], "nom": "Association des Hommes", "code": "HOMMES"})
                a_f = await mutation_engine.create_record(session, "Association", {"paroisse_id": p["id"], "nom": "Association des Femmes", "code": "FEMMES"})
                a_j = await mutation_engine.create_record(session, "Association", {"paroisse_id": p["id"], "nom": "Association des Jeunes", "code": "JEUNES"})
                a_s = await mutation_engine.create_record(session, "Association", {"paroisse_id": p["id"], "nom": "École du Sabbat", "code": "ECOLE_SABBAT"})

                for a in (a_h, a_f, a_j, a_s):
                    a["paroisse_id"] = p["id"]
                    assocs.append(a)

                parish_assoc_map[p["id"]] = {
                    "HOMMES": a_h,
                    "FEMMES": a_f,
                    "JEUNES": a_j,
                    "ECOLE_SABBAT": a_s,
                }

            logger.info("Seeding Foundational 4 Membres for test regression safety...")
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

            membres = [m1, m2, m3, m4]

            # Generate additional members up to target_member_count (100)
            logger.info(f"Generating additional members up to {target_member_count}...")
            count_to_generate = max(0, target_member_count - len(membres))

            base_year = 2026
            for i in range(1, count_to_generate + 1):
                # Deterministic distribution across parishes and zones
                target_parish = paroisses[i % len(paroisses)]
                avail_zones = parish_zones_map[target_parish["id"]]
                target_zone = avail_zones[i % len(avail_zones)]

                # Alternate gender and marital status
                is_female = (i % 2 == 0)
                sexe = "FEMME" if is_female else "HOMME"
                nom = FAMILY_NAMES[(i + 4) % len(FAMILY_NAMES)]
                prenom = (FIRST_NAMES_FEMALE if is_female else FIRST_NAMES_MALE)[(i // 2) % len(FIRST_NAMES_FEMALE)]

                # Birth year distribution (kids, youth, adults, seniors)
                age = 6 + (i * 7) % 70
                birth_year = base_year - age
                birth_month = 1 + (i % 12)
                birth_day = 1 + (i % 28)
                date_naissance = f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d}"

                statut_matrimonial = "MARIE" if (age >= 25 and (i % 3 != 0)) else "CELIBATAIRE"
                district = DISTRICTS[i % len(DISTRICTS)]
                adresse = f"Lot {i % 50 + 1} {chr(65 + (i % 26))} {district}"

                new_m = await mutation_engine.create_record(session, "Membre", {
                    "paroisse_id": target_parish["id"],
                    "zone_geographique_id": target_zone["id"],
                    "nom": nom,
                    "prenom": prenom,
                    "adresse": adresse,
                    "sexe": sexe,
                    "date_naissance": date_naissance,
                    "statut_matrimonial": statut_matrimonial,
                })
                membres.append(new_m)

            logger.info(f"Seeding Adhésions for {len(membres)} Membres...")
            adhesions = []
            # Keep initial test adhesions
            a_j1 = parish_assoc_map[p1["id"]]["JEUNES"]
            a_h1 = parish_assoc_map[p1["id"]]["HOMMES"]
            a_s2 = parish_assoc_map[p2["id"]]["ECOLE_SABBAT"]

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
            adhesions.extend([adh1, adh2, adh3])

            # Assign associations to ~75% of remaining members according to business rules
            # Leave ~20% without association (like m2 Rasoa Marie) so the agent can accurately detect unassigned members
            for idx, member in enumerate(membres[4:], 5):
                # Leave every 5th member without association
                if idx % 5 == 0:
                    continue

                parish_id = member.get("paroisse_id")
                assoc_set = parish_assoc_map.get(parish_id, parish_assoc_map[p1["id"]])

                b_date = datetime.date.fromisoformat(member["date_naissance"])
                approx_age = base_year - b_date.year

                # Apply BR-003, BR-004, BR-005:
                if approx_age < 16:
                    target_assoc = assoc_set["ECOLE_SABBAT"]
                elif member["statut_matrimonial"] == "CELIBATAIRE":
                    target_assoc = assoc_set["JEUNES"]
                elif member["sexe"] == "HOMME":
                    target_assoc = assoc_set["HOMMES"]
                else:
                    target_assoc = assoc_set["FEMMES"]

                adh_rec = await mutation_engine.create_record(session, "AdhesionAssociation", {
                    "membre_id": member["id"],
                    "association_id": target_assoc["id"],
                    "date_adhesion": f"{max(2015, b_date.year + 16):04d}-01-15",
                })
                adhesions.append(adh_rec)

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
            # Add additional transfer requests
            dp2 = await mutation_engine.create_record(session, "DemandePassage", {
                "membre_id": membres[5]["id"],
                "paroisse_origine_id": p2["id"],
                "paroisse_destination_id": p3["id"],
                "date_demande": "2025-01-10",
                "date_debut_passage": "2025-02-01",
                "date_fin_passage": "2025-03-01",
                "statut": "EN_ATTENTE",
            })
            demandes_passage = [dp1, dp2]

            logger.info("Seeding Historique des Rattachements...")
            hr1 = await mutation_engine.create_record(session, "HistoriqueRattachement", {
                "membre_id": m1["id"],
                "nouvelle_paroisse_id": p1["id"],
                "nouvelle_zone_id": z1_1["id"],
                "date_effet": "2020-01-01",
            })
            hr2 = await mutation_engine.create_record(session, "HistoriqueRattachement", {
                "membre_id": membres[6]["id"],
                "nouvelle_paroisse_id": p3["id"],
                "nouvelle_zone_id": z3_1["id"],
                "date_effet": "2022-06-15",
            })
            historiques = [hr1, hr2]

            logger.info(
                f"Seeding terminé avec succès ! "
                f"({len(membres)} membres, {len(adhesions)} adhésions, "
                f"{len(paroisses)} paroisses, {len(zones)} zones, {len(assocs)} associations)"
            )

            return {
                "paroisses": paroisses,
                "zones": zones,
                "associations": assocs,
                "membres": membres,
                "adhesions": adhesions,
                "demandes_passage": demandes_passage,
                "historiques": historiques,
            }
    finally:
        if close_session:
            await session.close()


def main():
    asyncio.run(seed_database(target_member_count=100))


if __name__ == "__main__":
    main()
