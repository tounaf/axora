import asyncio
import sys
from pathlib import Path
from axora.agent.runtime import AgentRuntime
from axora.config import settings
from axora.data.database import AsyncSessionLocal
from axora.data.dynamic_models import build_dynamic_tables
from axora.llm.provider import get_llm_adapter
from axora.semantic.service import SemanticModelService
from axora.tools.create_record import CreateRecordTool
from axora.tools.discover_model import DiscoverModelTool
from axora.tools.query_data import QueryDataTool
from axora.tools.registry import ToolRegistry
from axora.tools.update_record import UpdateRecordTool


async def run_cli():
    llm_adapter = get_llm_adapter()

    print("=" * 60)
    print("   AXORA INTERACTIVE CLI — From intent to action.")
    print("=" * 60)
    print(f"[*] Loaded Provider: {llm_adapter.provider_name}")
    print(f"[*] Loaded Model:    {llm_adapter.model_name}")

    yaml_path = Path("src/axora/semantic/definitions/gestion_paroissiale.yaml")
    if not yaml_path.is_file():
        print(f"[!] Error: Semantic model file not found at {yaml_path}")
        sys.exit(1)

    semantic_service = SemanticModelService.from_yaml(yaml_path)
    build_dynamic_tables(semantic_service)

    registry = ToolRegistry()
    registry.register(DiscoverModelTool(semantic_service))
    registry.register(QueryDataTool(semantic_service, AsyncSessionLocal))
    registry.register(CreateRecordTool(semantic_service, AsyncSessionLocal))
    registry.register(UpdateRecordTool(semantic_service, AsyncSessionLocal))

    runtime = AgentRuntime(tool_registry=registry, llm_adapter=llm_adapter)

    print(f"[*] Semantic Model:  {semantic_service.model_name} (v{semantic_service.version})")
    print(f"[*] Registered Tools: {[t.name for t in registry.list_tools()]}")
    print("-" * 60)
    print("Tapez vos intentions métier ou 'exit' pour quitter.\n")

    history: list[dict[str, str]] = []

    while True:
        try:
            user_input = input("Axora User > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("[*] Fermeture du CLI Axora. Au revoir!")
                break

            print("[*] Traitement par le Runtime Agent...")
            response = await runtime.process_intent(user_input, history=history)

            print(f"\nAxora Agent > {response}\n")
            print("-" * 60)

            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

        except (KeyboardInterrupt, EOFError):
            print("\n[*] Fermeture du CLI Axora.")
            break


def main():
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
