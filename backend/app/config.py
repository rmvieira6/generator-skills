"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SAI Library / LLM settings
    sai_api_key: str = ""
    sai_base_url: str = "https://api.sai.stefanini.com/v1"
    sai_model: str = "auto"
    sai_timeout: int = 120

    # Fallback: generic OpenAI-compatible endpoint (used when SAI Library is unavailable)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"

    # Server
    cors_origins: list[str] = ["http://localhost:8501", "http://127.0.0.1:8501"]
    debug: bool = False

    # Output
    tmp_dir: str = "/tmp/skill-forge"


settings = Settings()
