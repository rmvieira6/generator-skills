from __future__ import annotations

import logging
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Resolve .env a partir da raiz do monorepo (2 níveis acima de src/core/)
# Funciona independente de onde o processo foi iniciado.
_THIS_FILE = Path(__file__).resolve()          # .../apps/api/src/core/config.py
_MONOREPO_ROOT = _THIS_FILE.parents[4]         # .../generator-skills/
_API_ROOT = _THIS_FILE.parents[2]              # .../apps/api/

# Candidatos em ordem de prioridade: raiz do monorepo → apps/api/ → CWD
_ENV_CANDIDATES = [
    _MONOREPO_ROOT / ".env",
    _API_ROOT / ".env",
    Path.cwd() / ".env",
]
_ENV_FILE = next((str(p) for p in _ENV_CANDIDATES if p.exists()), str(_MONOREPO_ROOT / ".env"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    SAI_LIBRARY_BASE_URL: str = "https://sai-library.saiapplications.com"
    SAI_LIBRARY_API_KEY: str = ""
    SAI_LIBRARY_TEMPLATE_ID: str = ""

    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "change-me"
    DATABASE_URL: str = "sqlite:///./skillforge_history.db"
    MAX_UPLOAD_SIZE_MB: int = 20
    MAX_MATERIALS_PER_PROJECT: int = 20
    MAX_DESCRIPTION_LENGTH: int = 5000
    ALLOWED_ORIGINS: str = "http://localhost:8501,http://localhost:5173"

    AGENTS_CONFIG_PATH: str = "agents.yaml"
    CONNECTORS_CONFIG_PATH: str = "connectors.yaml"
    SKILL_MASTER_TEMPLATE_PATH: str = "packages/skill-master-template/SKILL.master.md"

    RETRY_ATTEMPTS: int = Field(default=3, ge=1, le=5)

    @field_validator("SAI_LIBRARY_API_KEY", "SAI_LIBRARY_TEMPLATE_ID", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return str(v).strip() if v else ""

    @property
    def allowed_origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def workspace_root(self) -> Path:
        return _MONOREPO_ROOT

    @property
    def sai_configured(self) -> bool:
        return bool(self.SAI_LIBRARY_API_KEY) and bool(self.SAI_LIBRARY_TEMPLATE_ID)


settings = Settings()
