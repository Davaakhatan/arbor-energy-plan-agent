"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Arbor Energy Plan Agent"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "arbor"
    postgres_password: str = "arbor_dev"
    postgres_db: str = "arbor_energy"

    @computed_field  # type: ignore[misc]
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_db,
            )
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_db: int = 0

    @computed_field  # type: ignore[misc]
    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL."""
        if self.redis_password:
            return str(
                RedisDsn.build(
                    scheme="redis",
                    password=self.redis_password,
                    host=self.redis_host,
                    port=self.redis_port,
                    path=str(self.redis_db),
                )
            )
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Security
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Performance
    recommendation_timeout_seconds: float = 2.0
    cache_ttl_seconds: int = 3600  # 1 hour

    # External APIs
    supplier_api_url: str | None = None
    usage_data_api_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
