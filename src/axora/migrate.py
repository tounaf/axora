import asyncio
from axora.data.migrations import migrate_cli_main

if __name__ == "__main__":
    print("=" * 60)
    print("   AXORA AUTOMATIC SCHEMA MIGRATION CLI")
    print("=" * 60)
    asyncio.run(migrate_cli_main())
    print("[*] Migration de la base de données exécutée avec succès !")
