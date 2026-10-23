import asyncio
import sys
from pathlib import Path
from axora.config import settings
from axora.semantic.service import SemanticModelService
from axora.tools.discover_model import DiscoverModelTool
from axora.tools.registry import ToolRegistry


async def run_cli():
    print("=" * 60)
    print("   AXORA INTERACTIVE CLI — From intent to action.")
    print("=" * 60)
    print(f"[*] Loaded Provider: {settings.LLM_PROVIDER}")
    print(f"[*] Loaded Model:    {settings.LLM_MODEL}")

    yaml_path = Path("src/axora/semantic/definitions/gestion_paroissiale.yaml")
    if not yaml_path.is_file():
        print(f"[!] Error: Semantic model file not found at {yaml_path}")
        sys.exit(1)

    semantic_service = SemanticModelService.from_yaml(yaml_path)
    discover_tool = DiscoverModelTool(semantic_service)

    registry = ToolRegistry()
    registry.register(discover_tool)

    print(f"[*] Semantic Model: {semantic_service.model_name} (v{semantic_service.version})")
    print(f"[*] Registered Tools: {[t.name for t in registry.list_tools()]}")
    print("-" * 60)
    print("Tapez vos intentions ou 'exit' pour quitter le CLI.\n")

    while True:
        try:
            user_input = input("Axora User > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("[*] Fermeture du CLI Axora. Au revoir!")
                break

            print(f"[*] Traitement de l'intention: '{user_input}'...")

            # Simulated agent execution step with registered tools
            if "paroisse" in user_input.lower() or "membre" in user_input.lower() or "zone" in user_input.lower():
                result = await discover_tool.execute({"include": ["attributes"]})
                entities = [e["name"] for e in result.data["entities"]]
                print(f"[Agent Response] Découverte sémantique effectuée. Entités disponibles: {entities}")
            else:
                print("[Agent Response] Intention reçue. Veuillez utiliser le moteur de requêtes ou préciser le concept.")

            print("-" * 60)

        except (KeyboardInterrupt, EOFError):
            print("\n[*] Fermeture du CLI Axora.")
            break


def main():
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
