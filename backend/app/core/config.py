from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = "development"
    database_url: str = "postgresql+asyncpg://noted:noted@localhost:5433/noted"
    redis_url: str = "redis://localhost:6380/0"

    jwt_secret: str = "change-me-generate-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    cookie_secure: bool = False
    cookie_domain: str | None = None

    cors_origins: list[str] = ["http://localhost:3000"]

    itunes_country: str = "us"
    itunes_cache_ttl_seconds: int = 60 * 60 * 24


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
