"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import computed_field
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
    environment: Literal["development", "staging", "production", "test"] = "development"
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
        # URL-encode username and password for special characters
        encoded_user = quote_plus(self.postgres_user)
        encoded_password = quote_plus(self.postgres_password)
        return f"postgresql+asyncpg://{encoded_user}:{encoded_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_db: int = 0
    redis_ssl: bool = False  # Enable for AWS ElastiCache with encryption in transit

    @computed_field  # type: ignore[misc]
    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL."""
        # Use rediss:// for SSL/TLS connections (AWS ElastiCache)
        scheme = "rediss" if self.redis_ssl else "redis"
        if self.redis_password:
            # URL-encode password for special characters
            encoded_password = quote_plus(self.redis_password)
            return f"{scheme}://:{encoded_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"{scheme}://{self.redis_host}:{self.redis_port}/{self.redis_db}"

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
