from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Settings
    PROJECT_NAME: str = "Axora"
    API_V1_PREFIX: str = "/api/v1"

    # Database Settings
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@db:5432/axora"

    # LLM Settings
    LLM_PROVIDER: str = "mock"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"

    # Agent Loop Settings
    MAX_AGENT_ITERATIONS: int = 8


settings = Settings()
