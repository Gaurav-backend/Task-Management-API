import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    google_client_id: str
    google_client_secret: str
    session_secret_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        secrets_dir="/run/secrets",
        extra="ignore",
        )
settings = Settings(
    _env_file=None if os.getenv("APP_ENV") == "production" else ".env"
)