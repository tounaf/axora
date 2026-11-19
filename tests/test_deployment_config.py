from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_compose_api_targets_postgres_internal_port_and_readiness():
    compose = yaml.safe_load((PROJECT_ROOT / "compose.yaml").read_text(encoding="utf-8"))
    api = compose["services"]["api"]
    database_url = api["environment"]["DATABASE_URL"]

    assert "@db:5432/" in database_url
    assert "@db:5431/" not in database_url
    assert "${POSTGRES_PASSWORD:?" in database_url
    assert "/health/ready" in api["healthcheck"]["test"][-1]
    assert api["depends_on"]["db"]["condition"] == "service_healthy"


def test_optional_admin_and_mysql_services_have_no_committed_passwords():
    compose = yaml.safe_load((PROJECT_ROOT / "compose.yaml").read_text(encoding="utf-8"))
    pgadmin = compose["services"]["pgadmin"]
    mysql = compose["services"]["mysql"]

    assert "admin" in pgadmin["profiles"]
    assert pgadmin["environment"]["PGADMIN_DEFAULT_PASSWORD"] == "${PGADMIN_DEFAULT_PASSWORD:-}"
    assert pgadmin["ports"] == ["127.0.0.1:8881:80"]
    assert mysql["environment"]["MYSQL_ROOT_PASSWORD"] == "${MYSQL_ROOT_PASSWORD:-}"
    assert mysql["environment"]["MYSQL_PASSWORD"] == "${MYSQL_PASSWORD:-}"
    assert "mysql" in mysql["profiles"]
    assert mysql["ports"] == ["127.0.0.1:3306:3306"]


def test_environment_example_uses_mock_and_contains_no_provider_credentials():
    lines = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
    values = {
        line.split("=", 1)[0]: line.split("=", 1)[1]
        for line in lines
        if "=" in line and not line.lstrip().startswith("#")
    }

    assert values["LLM_PROVIDER"] == "mock"
    assert values["POSTGRES_PASSWORD"] == ""
    for key in ("LLM_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "NVIDIA_API_KEY"):
        assert values[key] == ""
