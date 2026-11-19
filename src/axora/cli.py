import argparse
import asyncio
import sys
from pathlib import Path


def run_introspect(args: argparse.Namespace) -> None:
    """Executes database schema reverse-engineering into a semantic model YAML."""
    from axora.extensions.bdd.introspector import introspect_live_db, introspect_sql_file

    print("=" * 60)
    print("   AXORA SCHEMA INTROSPECTION & REVERSE-ENGINEERING")
    print("=" * 60)

    if args.sql_file:
        sql_path = Path(args.sql_file)
        if not sql_path.is_file():
            print(f"[!] Error: SQL file not found at {sql_path.absolute()}")
            sys.exit(1)

        model_name = args.name or sql_path.stem
        output_yaml = args.output or f"src/axora/semantic/definitions/{model_name}.yaml"

        print(f"[*] Parsing SQL DDL file: {sql_path}")
        print(f"[*] Target Model Name:   {model_name}")
        manifest = introspect_sql_file(sql_path, output_yaml=output_yaml, model_name=model_name)

    elif args.db_url:
        model_name = args.name or "live_db"
        output_yaml = args.output or f"src/axora/semantic/definitions/{model_name}.yaml"

        print(f"[*] Introspecting Live Database: {args.db_url}")
        print(f"[*] Target Model Name:          {model_name}")
        manifest = introspect_live_db(args.db_url, output_yaml=output_yaml, model_name=model_name)

    else:
        print("[!] Error: Either --sql-file or --db-url must be provided.")
        sys.exit(1)

    entities = manifest.get("model", {}).get("entities", {})
    print(f"[+] Introspection successful!")
    print(f"[+] Generated {len(entities)} semantic entities:")
    for entity_name, entity_def in sorted(entities.items()):
        storage_table = entity_def.get("storage", {}).get("table", "")
        rels = list(entity_def.get("relationships", {}).keys())
        print(f"    - {entity_name:18} (table: {storage_table:18} | {len(rels)} relationships)")

    print(f"\n[+] Manifest written to: {Path(output_yaml).resolve()}")
    print("=" * 60)


async def run_cli(model_file: str | None = None):
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

    llm_adapter = get_llm_adapter()

    print("=" * 60)
    print("   AXORA INTERACTIVE CLI — From intent to action.")
    print("=" * 60)
    print(f"[*] Loaded Provider: {llm_adapter.provider_name}")
    print(f"[*] Loaded Model:    {llm_adapter.model_name}")

    yaml_path = Path(model_file or "src/axora/semantic/definitions/gestion_paroissiale.yaml")
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
    parser = argparse.ArgumentParser(description="Axora CLI — Conversational Agent and Introspection Platform")
    subparsers = parser.add_subparsers(dest="subcommand")

    # Introspect subcommand
    parser_introspect = subparsers.add_parser("introspect", help="Reverse-engineer SQL schema into a semantic model YAML")
    source_group = parser_introspect.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--sql-file", type=str, help="Path to SQL dump or DDL file")
    source_group.add_argument("--db-url", type=str, help="Live database connection string")
    parser_introspect.add_argument("--output", "-o", type=str, help="Path to write generated YAML manifest")
    parser_introspect.add_argument("--name", "-n", type=str, help="Semantic model identifier")

    # Chat subcommand
    parser_chat = subparsers.add_parser("chat", help="Start conversational agent CLI")
    parser_chat.add_argument("--model-file", "-m", type=str, default="src/axora/semantic/definitions/gestion_paroissiale.yaml", help="Path to semantic model YAML")

    args = parser.parse_args()

    if args.subcommand == "introspect":
        run_introspect(args)
    else:
        model_file = getattr(args, "model_file", None)
        asyncio.run(run_cli(model_file))


if __name__ == "__main__":
    main()
