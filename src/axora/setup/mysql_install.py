from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import shlex
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from axora.progress import ProgressCallback, publish_progress

from axora.extensions.bdd.introspector import SQLDumpParser, introspect_sql_file

DEFAULT_STARTUP_TIMEOUT = 180
DEFAULT_IMPORT_TIMEOUT = 1800
MYSQL_PROJECT_NAME = "axora"
_MYSQL_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
_DUMP_DATABASE = re.compile(
    r"^\s*(?:CREATE\s+(?:DATABASE|SCHEMA)\s+(?:IF\s+NOT\s+EXISTS\s+)?|USE\s+)"
    r"(?:`((?:``|[^`])*)`|([A-Za-z0-9_$]+))",
    re.IGNORECASE | re.MULTILINE,
)
_CREATE_DATABASE = re.compile(
    r"^\s*CREATE\s+(?:DATABASE|SCHEMA)\b",
    re.IGNORECASE | re.MULTILINE,
)


class MysqlInstallError(RuntimeError):
    """Raised when the local MySQL installation workflow cannot continue safely."""


@dataclass(frozen=True)
class MysqlInstallPlan:
    sql_file: Path
    database_name: str
    model_name: str
    manifest_path: Path
    table_count: int
    sql_sha256: str
    database_created_by_dump: bool


@dataclass(frozen=True)
class MysqlInstallResult:
    database_name: str
    manifest_path: Path
    state_path: Path
    api_url: str
    reused_database: bool


def _validate_identifier(value: str, label: str) -> str:
    if not _MYSQL_IDENTIFIER.fullmatch(value):
        raise MysqlInstallError(
            f"Nom de {label} invalide : utilisez 1 à 64 caractères "
            "alphanumériques ou '_' et commencez par une lettre."
        )
    return value


def _default_database_name(sql_file: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9_]", "_", sql_file.stem)
    if not stem or not stem[0].isalpha():
        stem = f"axora_{stem}"
    return stem[:64]


def _read_sql_file(source: Path) -> str:
    if not source.is_file():
        raise MysqlInstallError(f"Fichier SQL introuvable : {source}")
    if not os.access(source, os.R_OK):
        raise MysqlInstallError(f"Fichier SQL illisible : {source}")
    try:
        return source.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise MysqlInstallError(f"Lecture du fichier SQL impossible : {source}") from exc


def _database_names_in_dump(sql_content: str) -> set[str]:
    without_comments = re.sub(r"/\*.*?\*/", " ", sql_content, flags=re.DOTALL)
    without_comments = re.sub(r"(?m)--\s.*$", " ", without_comments)
    names = set()
    for match in _DUMP_DATABASE.finditer(without_comments):
        names.add((match.group(1) or match.group(2) or "").replace("``", "`"))
    return names


def build_mysql_install_plan(
    sql_file: str | Path,
    database_name: str | None = None,
    model_name: str | None = None,
    manifest_path: str | Path | None = None,
    overwrite: bool = False,
) -> MysqlInstallPlan:
    source = Path(sql_file).expanduser().resolve()
    sql_content = _read_sql_file(source)
    default_name = _default_database_name(source)
    semantic_name = _validate_identifier(model_name or default_name, "modèle")

    parser = SQLDumpParser(sql_content, schema_name=semantic_name)
    schema = parser.introspect()
    if not schema.tables:
        raise MysqlInstallError(
            "Aucune instruction CREATE TABLE reconnue dans le fichier SQL ; "
            "le manifeste ne peut pas être généré."
        )

    embedded_database_names = _database_names_in_dump(sql_content)
    if len(embedded_database_names) > 1:
        raise MysqlInstallError(
            "Le dump référence plusieurs bases avec CREATE DATABASE/USE. "
            "Ce prototype accepte une seule base par installation."
        )
    embedded_database = next(iter(embedded_database_names), None)
    if database_name and embedded_database and database_name.lower() != embedded_database.lower():
        raise MysqlInstallError(
            f"Le dump cible la base '{embedded_database}', qui ne correspond pas à "
            f"--database '{database_name}'. Choisissez le nom correspondant au dump."
        )
    db_name = _validate_identifier(database_name or embedded_database or default_name, "base")

    target_manifest = Path(
        manifest_path or Path("src/axora/semantic/definitions") / f"{semantic_name}.yaml"
    ).expanduser().resolve()
    if not target_manifest.parent.is_dir():
        raise MysqlInstallError(
            f"Le dossier parent du manifeste n'existe pas : {target_manifest.parent}"
        )
    if not os.access(target_manifest.parent, os.W_OK):
        raise MysqlInstallError(
            f"Le dossier du manifeste n'est pas accessible en écriture : {target_manifest.parent}"
        )
    if target_manifest.exists() and not overwrite:
        raise MysqlInstallError(
            f"Le manifeste existe déjà : {target_manifest}. "
            "Choisissez un autre chemin ou confirmez son remplacement avec --overwrite."
        )

    return MysqlInstallPlan(
        sql_file=source,
        database_name=db_name,
        model_name=semantic_name,
        manifest_path=target_manifest,
        table_count=len(schema.tables),
        sql_sha256=hashlib.sha256(sql_content.encode("utf-8")).hexdigest(),
        database_created_by_dump=bool(_CREATE_DATABASE.search(sql_content)),
    )


def _run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    stdin: BinaryIO | None = None,
    timeout: int,
) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            stdin=stdin,
            capture_output=True,
            env=env,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise MysqlInstallError(
            "Docker CLI introuvable. Installez Docker et relancez la commande."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise MysqlInstallError(
            f"La commande Docker a dépassé le délai autorisé ({timeout} s)."
        ) from exc


def _project_root() -> Path:
    root = Path(__file__).resolve().parents[3]
    if not (root / "compose.yaml").is_file() or not (root / "Dockerfile").is_file():
        raise MysqlInstallError(
            "compose.yaml ou Dockerfile introuvable. Lancez cette commande depuis une installation Axora complète."
        )
    return root


def check_docker() -> str:
    root = _project_root()
    result = _run(
        ["docker", "info", "--format", "{{.ServerVersion}}"],
        cwd=root,
        timeout=15,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise MysqlInstallError(
            "Docker est installé mais son daemon est inaccessible. "
            f"Vérifiez son état et les permissions de l'utilisateur. {detail[:500]}"
        )
    return result.stdout.decode("utf-8", errors="replace").strip()


def _check_compose(cwd: Path) -> str:
    result = _run(
        ["docker", "compose", "version", "--short"],
        cwd=cwd,
        timeout=15,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise MysqlInstallError(
            f"Le plugin Docker Compose est inaccessible. {detail[:500]}"
        )
    return result.stdout.decode("utf-8", errors="replace").strip()


def check_compose() -> str:
    return _check_compose(_project_root())


def _compose_command(state_path: Path, *args: str) -> list[str]:
    compose_path = _project_root() / "compose.yaml"
    return [
        "docker", "compose",
        "--project-name", MYSQL_PROJECT_NAME,
        "--file", str(compose_path),
        "--env-file", str(state_path),
        "--profile", "mysql-agent",
        *args,
    ]


def _ensure_private_state_dir(state_dir: Path) -> None:
    existed = state_dir.exists()
    try:
        state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        directory_mode = stat.S_IMODE(state_dir.stat().st_mode)
    except OSError as exc:
        raise MysqlInstallError(f"Impossible de créer le dossier de configuration : {state_dir}") from exc
    if directory_mode & 0o077:
        reason = "existant" if existed else "créé"
        raise MysqlInstallError(
            f"Le dossier de configuration {reason} n'est pas privé "
            f"(permissions {directory_mode:04o}) : {state_dir}. "
            "Restreignez ses permissions à l'utilisateur courant."
        )


def _write_private_file(path: Path, content: str) -> None:
    temporary_path = path.with_name(f".{path.name}.{secrets.token_hex(4)}.tmp")
    try:
        descriptor = os.open(temporary_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write(content)
        os.replace(temporary_path, path)
        os.chmod(path, 0o600)
    except OSError as exc:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise MysqlInstallError(f"Impossible d'écrire le fichier privé : {path}") from exc


def _load_state(state_path: Path, host_port: int) -> dict[str, object]:
    if state_path.exists():
        try:
            state_mode = stat.S_IMODE(state_path.stat().st_mode)
        except OSError as exc:
            raise MysqlInstallError(f"Impossible d'inspecter l'état local : {state_path}") from exc
        if state_mode & 0o077:
            raise MysqlInstallError(
                f"L'état local n'est pas privé (permissions {state_mode:04o}) : {state_path}. "
                "Restreignez ses permissions à l'utilisateur courant."
            )
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MysqlInstallError(
                f"État d'installation Axora illisible : {state_path}. "
                "Ne supprimez pas le volume MySQL ; restaurez ou inspectez cet état."
            ) from exc
        if (
            not isinstance(state, dict)
            or not state.get("mysql_root_password")
            or not state.get("mysql_password")
            or not state.get("mysql_bootstrap_database")
        ):
            raise MysqlInstallError(
                f"État d'installation incomplet : {state_path}. Aucun volume n'a été modifié."
            )
        if state.get("host_port") != host_port:
            raise MysqlInstallError(
                f"Cette instance MySQL utilise déjà le port {state.get('host_port')}. "
                "Relancez avec le même --port pour réutiliser son Compose."
            )
        databases = state.setdefault("databases", {})
        if not isinstance(databases, dict):
            raise MysqlInstallError(f"État des bases invalide : {state_path}")
        return state

    return {
        "mysql_root_password": secrets.token_urlsafe(32),
        "mysql_password": secrets.token_urlsafe(32),
        "mysql_bootstrap_database": f"axora_bootstrap_{secrets.token_hex(4)}",
        "host_port": host_port,
        "databases": {},
    }


def _write_compose_env(
    env_path: Path,
    *,
    state_path: Path,
    state: dict[str, object],
    plan: MysqlInstallPlan,
    api_port: int,
) -> None:
    values = {
        "POSTGRES_USER": "axora",
        "POSTGRES_PASSWORD": str(state.setdefault("postgres_placeholder_password", secrets.token_urlsafe(32))),
        "POSTGRES_DB": "axora",
        "MYSQL_ROOT_PASSWORD": str(state["mysql_root_password"]),
        "MYSQL_PASSWORD": str(state["mysql_password"]),
        "MYSQL_USER": "axora",
        "MYSQL_DATABASE": str(state["mysql_bootstrap_database"]),
        "MYSQL_PORT": str(state["host_port"]),
        "API_PORT": str(api_port),
        "AXORA_DATABASE_NAME": plan.database_name,
        "AXORA_INSTALL_ENV_FILE": str(env_path.resolve()),
        "AXORA_API_ENV_FILE": str(env_path.resolve()),
        "AXORA_SEMANTIC_MODEL_HOST_PATH": str(plan.manifest_path),
    }
    _write_private_file(
        env_path,
        "".join(f"{key}={shlex.quote(value)}\n" for key, value in values.items()),
    )
    state["database_name"] = plan.database_name
    state["manifest_path"] = str(plan.manifest_path)
    state["api_port"] = api_port
    state["database_engine"] = "mysql"
    state["database_user"] = "axora"
    state["database_password"] = state["mysql_password"]
    _write_private_file(
        state_path,
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    )


def _run_compose(
    command: list[str],
    *,
    cwd: Path,
    timeout: int,
    stdin: BinaryIO | None = None,
) -> subprocess.CompletedProcess[bytes]:
    result = _run(command, cwd=cwd, stdin=stdin, timeout=timeout)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise MysqlInstallError(f"La commande Docker Compose a échoué. {detail[:1000]}")
    return result


def _refuse_unmanaged_mysql(root: Path, state_dir: Path) -> None:
    containers = _run(
        ["docker", "ps", "--all", "--quiet", "--filter", "name=^/axora_mysql$"],
        cwd=root,
        timeout=30,
    )
    if containers.returncode != 0:
        detail = containers.stderr.decode("utf-8", errors="replace").strip()
        raise MysqlInstallError(f"Impossible d'inspecter les conteneurs Docker Axora. {detail[:500]}")
    volume = _run(
        [
            "docker", "volume", "ls", "--quiet",
            "--filter", "name=^axora_axora-mysql-data$",
        ],
        cwd=root,
        timeout=30,
    )
    if volume.returncode != 0:
        detail = volume.stderr.decode("utf-8", errors="replace").strip()
        raise MysqlInstallError(f"Impossible d'inspecter le volume MySQL Axora. {detail[:500]}")
    if containers.stdout.strip() or volume.stdout.strip():
        raise MysqlInstallError(
            "Un conteneur MySQL ou un volume Compose Axora existe déjà, mais aucun état "
            f"privé correspondant n'a été trouvé dans {state_dir}. "
            "Aucune ressource n'a été modifiée ; restaurez l'état ou inspectez le volume."
        )


def _mysql_exec(
    compose_command: list[str],
    cwd: Path,
    sql: str,
    timeout: int = 60,
) -> str:
    result = _run_compose(
        [
            *compose_command,
            "exec", "--no-TTY", "mysql",
            "sh", "-c",
            'export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"; exec mysql --user=root --batch --skip-column-names --execute "$1"',
            "axora-mysql",
            sql,
        ],
        cwd=cwd,
        timeout=timeout,
    )
    return result.stdout.decode("utf-8", errors="replace").strip()


def _install_mysql_from_dump(
    plan: MysqlInstallPlan,
    *,
    host_port: int = 3307,
    api_port: int = 8001,
    startup_timeout: int = DEFAULT_STARTUP_TIMEOUT,
    import_timeout: int = DEFAULT_IMPORT_TIMEOUT,
    state_dir: str | Path | None = None,
    overwrite: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> MysqlInstallResult:
    publish_progress(
        progress_callback,
        phase="installation",
        status="started",
        message="Vérification des prérequis et de l'état local…",
    )
    if not 1024 <= host_port <= 65535 or not 1024 <= api_port <= 65535:
        raise MysqlInstallError("Les ports locaux doivent être compris entre 1024 et 65535.")
    if host_port == api_port:
        raise MysqlInstallError("Les ports MySQL et API doivent être différents.")
    if startup_timeout <= 0 or import_timeout <= 0:
        raise MysqlInstallError("Les délais d'attente doivent être positifs.")
    if plan.manifest_path.exists() and not overwrite:
        raise MysqlInstallError(
            f"Le manifeste existe déjà : {plan.manifest_path}. "
            "Choisissez un autre chemin ou utilisez --overwrite."
        )
    sql_content = _read_sql_file(plan.sql_file)
    current_sha256 = hashlib.sha256(sql_content.encode("utf-8")).hexdigest()
    if current_sha256 != plan.sql_sha256:
        raise MysqlInstallError("Le fichier SQL a changé depuis la création du plan. Recréez le plan.")

    root = _project_root()
    compose_version = _check_compose(root)
    server_version = check_docker()
    publish_progress(
        progress_callback,
        phase="installation",
        status="completed",
        message=f"Docker {server_version} et Compose {compose_version} sont disponibles.",
    )
    install_state_dir = Path(
        state_dir or Path.home() / ".config" / "axora" / "installations"
    ).expanduser().resolve()
    _ensure_private_state_dir(install_state_dir)
    state_path = install_state_dir / "mysql-compose.json"
    env_path = install_state_dir / "mysql-compose.env"
    state_existed = state_path.exists()
    state = _load_state(state_path, host_port)
    databases = state.get("databases")
    if not isinstance(databases, dict):
        raise MysqlInstallError(f"État des bases invalide : {state_path}")

    recorded_import = databases.get(plan.database_name)
    reused_database = False
    if recorded_import is not None:
        if not isinstance(recorded_import, dict) or recorded_import.get("sql_sha256") != plan.sql_sha256:
            raise MysqlInstallError(
                f"La base '{plan.database_name}' est déjà gérée mais son dump diffère. "
                "Choisissez un autre nom de base pour préserver les données existantes."
            )
        reused_database = True

    if not state_existed:
        _refuse_unmanaged_mysql(root, install_state_dir)
    _write_compose_env(env_path, state_path=state_path, state=state, plan=plan, api_port=api_port)
    compose = _compose_command(env_path)
    config = _run_compose(
        [*compose, "config", "--quiet"],
        cwd=root,
        timeout=30,
    )
    del config

    print(f"Docker {server_version} et Compose {compose_version} détectés.")
    print("Démarrage/réutilisation des services MySQL Axora depuis compose.yaml.")
    publish_progress(
        progress_callback,
        phase="installation",
        status="started",
        message="Démarrage ou réutilisation du service MySQL…",
    )
    _run_compose(
        [*compose, "up", "--detach", "--wait", "--wait-timeout", str(startup_timeout), "mysql"],
        cwd=root,
        timeout=startup_timeout + 30,
    )
    publish_progress(
        progress_callback,
        phase="installation",
        status="completed",
        message="Service MySQL disponible.",
    )

    if not reused_database:
        publish_progress(
            progress_callback,
            phase="installation",
            status="started",
            message="Import du fichier SQL dans la base cible…",
        )
        existing_schema = _mysql_exec(
            compose,
            root,
            "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA "
            f"WHERE SCHEMA_NAME = '{plan.database_name}'",
        )
        if existing_schema:
            raise MysqlInstallError(
                f"La base '{plan.database_name}' existe déjà dans le volume MySQL Axora. "
                "Aucune importation n'a été faite ; choisissez une nouvelle valeur avec --database."
            )

        if not plan.database_created_by_dump:
            _mysql_exec(
                compose,
                root,
                f"CREATE DATABASE `{plan.database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci",
            )
        _mysql_exec(
            compose,
            root,
            f"GRANT ALL PRIVILEGES ON `{plan.database_name}`.* TO 'axora'@'%'",
        )
        try:
            with plan.sql_file.open("rb") as sql_stream:
                _run_compose(
                    [
                        *compose,
                        "exec", "--no-TTY", "mysql",
                        "sh", "-c",
                        'export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"; exec mysql --user=root --database="$1"',
                        "axora-mysql",
                        plan.database_name,
                    ],
                    cwd=root,
                    stdin=sql_stream,
                    timeout=import_timeout,
                )
        except MysqlInstallError as exc:
            raise MysqlInstallError(
                f"Échec de l'import SQL. Le projet Compose et le volume MySQL "
                f"sont conservés pour diagnostic. {exc}"
            ) from exc
        except OSError as exc:
            raise MysqlInstallError(f"Lecture du fichier SQL impossible : {plan.sql_file}") from exc

        databases[plan.database_name] = {
            "sql_sha256": plan.sql_sha256,
            "manifest_path": str(plan.manifest_path),
        }
        _write_compose_env(
            env_path,
            state_path=state_path,
            state=state,
            plan=plan,
            api_port=api_port,
        )
        publish_progress(
            progress_callback,
            phase="installation",
            status="completed",
            message="Import SQL terminé.",
        )
    else:
        publish_progress(
            progress_callback,
            phase="installation",
            status="completed",
            message="Base déjà importée : réutilisation sans nouvel import.",
        )

    publish_progress(
        progress_callback,
        phase="installation",
        status="started",
        message="Génération du manifeste sémantique…",
    )
    try:
        introspect_sql_file(
            plan.sql_file,
            output_yaml=plan.manifest_path,
            model_name=plan.model_name,
        )
    except (OSError, ValueError) as exc:
        raise MysqlInstallError(
            f"L'import a réussi, mais la génération du manifeste a échoué : {exc}. "
            "La base est conservée pour reprise."
        ) from exc
    publish_progress(
        progress_callback,
        phase="installation",
        status="completed",
        message="Manifeste sémantique généré.",
    )

    _write_compose_env(env_path, state_path=state_path, state=state, plan=plan, api_port=api_port)
    compose = _compose_command(env_path)
    publish_progress(
        progress_callback,
        phase="installation",
        status="started",
        message="Démarrage de l'API Axora et vérification de sa disponibilité…",
    )
    _run_compose(
        [
            *compose,
            "up", "--detach", "--build", "--wait", "--wait-timeout",
            str(startup_timeout), "mysql", "api-mysql",
        ],
        cwd=root,
        timeout=startup_timeout + 300,
    )
    publish_progress(
        progress_callback,
        phase="installation",
        status="completed",
        message="API Axora disponible.",
    )

    _write_private_file(
        state_path,
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    )
    return MysqlInstallResult(
        database_name=plan.database_name,
        manifest_path=plan.manifest_path,
        state_path=state_path,
        api_url=f"http://127.0.0.1:{api_port}",
        reused_database=reused_database,
    )


def install_mysql_from_dump(
    plan: MysqlInstallPlan,
    *,
    host_port: int = 3307,
    api_port: int = 8001,
    startup_timeout: int = DEFAULT_STARTUP_TIMEOUT,
    import_timeout: int = DEFAULT_IMPORT_TIMEOUT,
    state_dir: str | Path | None = None,
    overwrite: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> MysqlInstallResult:
    publish_progress(
        progress_callback,
        phase="installation",
        status="started",
        message="Démarrage du parcours d'installation Axora…",
    )
    try:
        result = _install_mysql_from_dump(
            plan,
            host_port=host_port,
            api_port=api_port,
            startup_timeout=startup_timeout,
            import_timeout=import_timeout,
            state_dir=state_dir,
            overwrite=overwrite,
            progress_callback=progress_callback,
        )
    except MysqlInstallError:
        publish_progress(
            progress_callback,
            event_type="error",
            phase="installation",
            status="failed",
            message="L'installation Axora a échoué ; les ressources existantes sont conservées.",
        )
        raise
    publish_progress(
        progress_callback,
        event_type="completed",
        phase="installation",
        status="completed",
        message="Installation Axora terminée.",
    )
    return result
