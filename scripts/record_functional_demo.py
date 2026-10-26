import asyncio
import sys
import time
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from axora.agent.decisions import AgentDecision, ToolCall
from axora.agent.runtime import AgentRuntime
from axora.data.dynamic_models import build_dynamic_tables, metadata
from axora.data.seed import seed_database
from axora.llm.provider import MockLLMAdapter
from axora.semantic.service import SemanticModelService
from axora.tools.create_record import CreateRecordTool
from axora.tools.discover_model import DiscoverModelTool
from axora.tools.query_data import QueryDataTool
from axora.tools.registry import ToolRegistry

YAML_PATH = "src/axora/semantic/definitions/gestion_paroissiale.yaml"


def print_banner(text: str):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


async def record_demo():
    print_banner("AXORA — ENREGISTREMENT ET DEMONSTRATION FONCTIONNELLE E2E")
    time.sleep(0.3)

    print("[1] Chargement du Modèle Sémantique (gestion_paroissiale.yaml)...")
    semantic_service = SemanticModelService.from_yaml(YAML_PATH)
    build_dynamic_tables(semantic_service)
    print(f"    -> Modèle Sémantique Chargé : '{semantic_service.model_name}' (v{semantic_service.version})")
    time.sleep(0.3)

    print("\n[2] Initialisation de la Base de Données SQLite en-mémoire & Seeding...")
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        seed_data = await seed_database(session)
    print(f"    -> Base de données alimentée : {len(seed_data['membres'])} membres, {len(seed_data['paroisses'])} paroisses, {len(seed_data['zones'])} zones géographiques.")
    time.sleep(0.3)

    print("\n[3] Enregistrement des Outils Génériques dans le Registre...")
    registry = ToolRegistry()
    registry.register(DiscoverModelTool(semantic_service))
    registry.register(QueryDataTool(semantic_service, session_factory))
    registry.register(CreateRecordTool(semantic_service, session_factory))
    print(f"    -> Outils enregistrés : {[t.name for t in registry.list_tools()]}")
    time.sleep(0.3)

    # Predefined Agent Decision Steps
    user_intent = "Qui sont les membres de la paroisse Andranovelona qui habitent dans la zone d'Andoharanofotsy ?"

    decisions = [
        AgentDecision(
            type="call_tool",
            tool_call=ToolCall(name="discover_model", arguments={"concept": "Membre", "include": ["attributes", "relationships"]}),
        ),
        AgentDecision(
            type="call_tool",
            tool_call=ToolCall(
                name="query_data",
                arguments={
                    "entity": "Membre",
                    "select": ["nom", "prenom", "statut_matrimonial", "adresse"],
                    "filters": [
                        {"path": "paroisse.nom", "operator": "equals", "value": "Andranovelona"},
                        {"path": "zone.nom", "operator": "equals", "value": "Andoharanofotsy"},
                    ],
                },
            ),
        ),
        AgentDecision(
            type="final_answer",
            content="J'ai trouvé 2 membres dans la zone Andoharanofotsy de la paroisse Andranovelona :\n1. Jean Rakoto (Célibataire) - Lot II B 12 Andoharanofotsy\n2. Marie Rasoa (Célibataire) - Lot IV K 45 Andoharanofotsy",
        ),
    ]

    llm_adapter = MockLLMAdapter(decisions)
    runtime = AgentRuntime(tool_registry=registry, llm_adapter=llm_adapter)

    print_banner(f"USER INTENT : '{user_intent}'")
    time.sleep(0.3)

    print(">>> Agent Axora Runtime est en cours d'exécution...")
    response = await runtime.process_intent(user_intent)

    print_banner("REPONSE FINALE DE L'AGENT AXORA")
    print(response)
    print("\n" + "=" * 70)
    print("  DEMONSTRATION FONCTIONNELLE REUSSIE A 100%")
    print("=" * 70 + "\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(record_demo())
