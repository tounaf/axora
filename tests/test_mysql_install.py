import argparse
import json
import subprocess
from pathlib import Path

import pytest

from axora.cli import run_mysql_install
from axora.extensions.bdd.introspector import introspect_sql_file
from axora.setup.mysql_install import (
    MysqlInstallError,
    build_mysql_install_plan,
    check_docker,
    install_mysql_from_dump,
)
from axora.data.dynamic_models import build_dynamic_tables, get_dynamic_table
from axora.semantic.service import SemanticModelService


def _sql_dump(path: Path) -> Path:
    path.write_text(
        "CREATE TABLE `customer` (`id` INT PRIMARY KEY, `name` VARCHAR(80));\n",
        encoding="utf-8",
    )
    return path


def test_mysql_install_plan_detects_tables_without_side_effects(tmp_path):
    source = _sql_dump(tmp_path / "customers.sql")
    manifest = tmp_path / "customer-model.yaml"

    plan = build_mysql_install_plan(
        source,
        database_name="customers",
        model_name="customer_model",
        manifest_path=manifest,
    )

    assert plan.database_name == "customers"
    assert plan.model_name == "customer_model"
    assert plan.table_count == 1
    assert plan.manifest_path == manifest
    assert not manifest.exists()


def test_mysql_install_plan_rejects_sql_without_create_table(tmp_path):
    source = tmp_path / "empty.sql"
    source.write_text("SELECT 1;\n", encoding="utf-8")

    with pytest.raises(MysqlInstallError, match="Aucune instruction CREATE TABLE"):
        build_mysql_install_plan(source)


def test_mysql_install_plan_uses_embedded_database_name(tmp_path):
    source = tmp_path / "dump.sql"
    source.write_text(
        "CREATE DATABASE /*!32312 IF NOT EXISTS*/ `source_db`;\n"
        "USE `source_db`;\n"
        "CREATE TABLE `customer` (`id` INT PRIMARY KEY);\n",
        encoding="utf-8",
    )

    plan = build_mysql_install_plan(source)

    assert plan.database_name == "source_db"


def test_generated_manifest_preserves_integer_primary_key_type(tmp_path):
    source = tmp_path / "customers.sql"
    source.write_text(
        "CREATE TABLE `department` (`id` INT PRIMARY KEY, `name` VARCHAR(80));\n"
        "CREATE TABLE `customer` (`id` INT PRIMARY KEY, `department_id` INT, "
        "FOREIGN KEY (`department_id`) REFERENCES `department` (`id`));\n",
        encoding="utf-8",
    )
    manifest_path = tmp_path / "manifest.yaml"
    manifest = introspect_sql_file(source, output_yaml=manifest_path, model_name="customers")
    assert manifest["model"]["entities"]["Customer"]["storage"]["id_type"] == "integer"

    semantic_service = SemanticModelService.from_yaml(manifest_path)
    build_dynamic_tables(semantic_service)

    customer_table = get_dynamic_table("customer", semantic_service)
    assert customer_table.c.id.type.python_type is int


def test_mysql_install_plan_rejects_mismatched_embedded_database(tmp_path):
    source = tmp_path / "dump.sql"
    source.write_text(
        "USE `source_db`;\nCREATE TABLE `customer` (`id` INT PRIMARY KEY);\n",
        encoding="utf-8",
    )

    with pytest.raises(MysqlInstallError, match="ne correspond pas"):
        build_mysql_install_plan(source, database_name="another_db")


def test_mysql_install_plan_rejects_existing_manifest_without_overwrite(tmp_path):
    source = _sql_dump(tmp_path / "customers.sql")
    manifest = tmp_path / "model.yaml"
    manifest.write_text("existing: true\n", encoding="utf-8")

    with pytest.raises(MysqlInstallError, match="existe déjà"):
        build_mysql_install_plan(source, manifest_path=manifest)


def test_check_docker_reports_missing_cli(monkeypatch):
    def missing_docker(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", missing_docker)

    with pytest.raises(MysqlInstallError, match="Docker CLI introuvable"):
        check_docker()


def test_cli_plan_does_not_start_mysql(tmp_path, monkeypatch, capsys):
    source = _sql_dump(tmp_path / "customers.sql")

    def unexpected_install(*args, **kwargs):
        raise AssertionError("plan mode must not provision MySQL")

    monkeypatch.setattr("axora.setup.mysql_install.check_docker", lambda: "27.2.0")
    monkeypatch.setattr("axora.setup.mysql_install.check_compose", lambda: "2.30.0")
    monkeypatch.setattr("axora.setup.mysql_install.install_mysql_from_dump", unexpected_install)

    run_mysql_install(
        argparse.Namespace(
            sql_file=str(source),
            database=None,
            name=None,
            output=str(tmp_path / "model.yaml"),
            overwrite=False,
            plan=True,
            yes=False,
            port=3307,
            api_port=8001,
            startup_timeout=180,
            import_timeout=1800,
            state_dir=str(tmp_path / "state"),
        )
    )

    output = capsys.readouterr().out
    assert "Mode plan" in output
    assert not (tmp_path / "model.yaml").exists()
    assert not (tmp_path / "state").exists()


def test_install_mysql_imports_dump_and_persists_private_state(tmp_path, monkeypatch):
    source = _sql_dump(tmp_path / "customers.sql")
    manifest = tmp_path / "customer-model.yaml"
    state_dir = tmp_path / "state"
    plan = build_mysql_install_plan(
        source,
        database_name="customers",
        model_name="customer_model",
        manifest_path=manifest,
    )
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        if command[1:3] == ["info", "--format"]:
            stdout = b"27.2.0"
        elif command[1:3] == ["compose", "version"]:
            stdout = b"2.30.0"
        elif "exec" in command:
            if kwargs.get("stdin"):
                assert kwargs["stdin"].read().startswith(b"CREATE TABLE")
            stdout = b""
        else:
            stdout = b""
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = install_mysql_from_dump(
        plan,
        host_port=13307,
        api_port=18001,
        startup_timeout=5,
        import_timeout=30,
        state_dir=state_dir,
    )

    commands = [call[0] for call in calls]
    mysql_up = next(
        command for command in commands
        if "up" in command and "api-mysql" not in command
    )
    api_up = commands[-1]
    assert mysql_up[:2] == ["docker", "compose"]
    assert "compose.yaml" in " ".join(mysql_up)
    assert "mysql" in mysql_up
    assert "api-mysql" in api_up
    assert "--build" in api_up and "--wait" in api_up
    env_file = Path(mysql_up[mysql_up.index("--env-file") + 1])
    env_content = env_file.read_text(encoding="utf-8")
    assert "MYSQL_ROOT_PASSWORD=" in env_content
    assert "AXORA_DATABASE_NAME=customers" in env_content
    assert "AXORA_SEMANTIC_MODEL_HOST_PATH=" in env_content
    assert manifest.is_file()
    assert "Customer:" in manifest.read_text(encoding="utf-8")
    assert result.api_url == "http://127.0.0.1:18001"
    assert not result.reused_database

    state = json.loads(result.state_path.read_text(encoding="utf-8"))
    assert state["database_engine"] == "mysql"
    assert state["database_name"] == "customers"
    assert state["database_user"] == "axora"
    assert state["manifest_path"] == str(manifest)
    assert state["database_password"]
    assert (state_dir / "mysql-compose.env").is_file()
    assert (state_dir / "mysql-compose.env").stat().st_mode & 0o777 == 0o600
    assert result.state_path.stat().st_mode & 0o777 == 0o600
    assert state_dir.stat().st_mode & 0o777 == 0o700


def test_install_mysql_stops_after_import_error_and_keeps_resources(tmp_path, monkeypatch):
    source = _sql_dump(tmp_path / "customers.sql")
    manifest = tmp_path / "customer-model.yaml"
    plan = build_mysql_install_plan(
        source,
        database_name="customers",
        manifest_path=manifest,
    )
    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        if command[1:3] == ["info", "--format"]:
            return subprocess.CompletedProcess(command, 0, stdout=b"27.2", stderr=b"")
        if command[1:3] == ["compose", "version"]:
            return subprocess.CompletedProcess(command, 0, stdout=b"2.30", stderr=b"")
        if "exec" in command and kwargs.get("stdin"):
            return subprocess.CompletedProcess(command, 1, stdout=b"", stderr=b"bad SQL")
        return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(MysqlInstallError, match="Échec de l'import SQL"):
        install_mysql_from_dump(
            plan,
            state_dir=tmp_path / "state",
            startup_timeout=5,
            import_timeout=30,
        )

    assert not manifest.exists()
    assert (tmp_path / "state").is_dir()
    assert (tmp_path / "state" / "mysql-compose.json").is_file()
    state = json.loads((tmp_path / "state" / "mysql-compose.json").read_text(encoding="utf-8"))
    assert state["databases"] == {}
    assert any(command[:2] == ["docker", "compose"] and "up" in command for command in commands)


def test_install_mysql_rejects_non_private_state_directory_before_starting_container(tmp_path, monkeypatch):
    source = _sql_dump(tmp_path / "customers.sql")
    plan = build_mysql_install_plan(
        source,
        database_name="customers",
        manifest_path=tmp_path / "model.yaml",
    )
    state_dir = tmp_path / "shared-state"
    state_dir.mkdir(mode=0o755)
    state_dir.chmod(0o755)
    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, stdout=b"27.2", stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(MysqlInstallError, match="n'est pas privé"):
        install_mysql_from_dump(plan, state_dir=state_dir)

    assert len(commands) == 2
    assert {command[1] for command in commands} == {"info", "compose"}


def test_install_mysql_reuses_compose_database_without_reimporting(tmp_path, monkeypatch):
    source = _sql_dump(tmp_path / "customers.sql")
    manifest = tmp_path / "customer-model.yaml"
    state_dir = tmp_path / "state"
    commands = []

    def fake_run(command, **kwargs):
        commands.append((command, kwargs))
        if command[1:3] == ["info", "--format"]:
            stdout = b"27.2.0"
        elif command[1:3] == ["compose", "version"]:
            stdout = b"2.30.0"
        else:
            stdout = b""
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    first_plan = build_mysql_install_plan(
        source,
        database_name="customers",
        model_name="customer_model",
        manifest_path=manifest,
    )
    first = install_mysql_from_dump(first_plan, state_dir=state_dir, startup_timeout=5)
    assert not first.reused_database

    start_index = len(commands)
    second_plan = build_mysql_install_plan(
        source,
        database_name="customers",
        model_name="customer_model",
        manifest_path=manifest,
        overwrite=True,
    )
    second = install_mysql_from_dump(
        second_plan,
        state_dir=state_dir,
        startup_timeout=5,
        overwrite=True,
    )
    second_calls = commands[start_index:]

    assert second.reused_database
    assert second.api_url == first.api_url
    assert all(kwargs.get("stdin") is None for _, kwargs in second_calls)
    assert not any(
        "SELECT SCHEMA_NAME" in command
        or "CREATE DATABASE" in command
        or "GRANT ALL" in command
        for command, _ in second_calls
    )
    assert any("api-mysql" in command for command, _ in second_calls)


def test_install_mysql_refuses_unmanaged_compose_volume(tmp_path, monkeypatch):
    source = _sql_dump(tmp_path / "customers.sql")
    plan = build_mysql_install_plan(
        source,
        database_name="customers",
        manifest_path=tmp_path / "customer-model.yaml",
    )
    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        if command[1:3] == ["info", "--format"]:
            stdout = b"27.2.0"
        elif command[1:3] == ["compose", "version"]:
            stdout = b"2.30.0"
        elif command[1:3] == ["volume", "ls"]:
            stdout = b"axora_axora-mysql-data\n"
        else:
            stdout = b""
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(MysqlInstallError, match="Aucune ressource n'a été modifiée"):
        install_mysql_from_dump(plan, state_dir=tmp_path / "state")

    assert not any("up" in command for command in commands)
