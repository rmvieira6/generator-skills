from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SAI_LIBRARY_BASE_URL: str = "https://sai-library.saiapplications.com"
    SAI_LIBRARY_API_KEY: str = ""
    SAI_LIBRARY_TEMPLATE_ID: str = ""

    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "change-me"
    DATABASE_URL: str = "sqlite:///./skillforge_history.db"
    MAX_UPLOAD_SIZE_MB: int = 20
    MAX_MATERIALS_PER_PROJECT: int = 20
    MAX_DESCRIPTION_LENGTH: int = 5000
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    AGENTS_CONFIG_PATH: str = "agents.yaml"
    CONNECTORS_CONFIG_PATH: str = "connectors.yaml"
    SKILL_MASTER_TEMPLATE_PATH: str = "packages/skill-master-template/SKILL.master.md"

    RETRY_ATTEMPTS: int = Field(default=3, ge=1, le=5)

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def workspace_root(self) -> Path:
        return Path.cwd()


settings = Settings()
