from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Asistente Financiero Familiar IA"
    api_prefix: str = "/api/v1"
    database_url: str | None = None
    mysql_url: str | None = None
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60 * 24
    upload_dir: str = "uploads"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def effective_database_url(self) -> str:
        url = self.database_url or self.mysql_url or "mysql+pymysql://family:family@mysql:3306/family_finance"
        if url.startswith("mysql://"):
            return url.replace("mysql://", "mysql+pymysql://", 1)
        return url

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
