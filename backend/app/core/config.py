"""Core configuration module using pydantic-settings."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase
    supabase_url: str = "https://placeholder.supabase.co"
    supabase_publishable_key: str = "placeholder"
    supabase_secret_key: SecretStr = Field(default="placeholder")

    # Google Gemini 3 Flash
    google_gemini_api_key: str = ""

    # Nano Banana Pro (Image Generation)
    nano_banana_api_key: str = ""

    # App
    secret_key: SecretStr = Field(default="dev-secret-key-change-in-production")
    allowed_origins: list[str] = Field(default=["http://localhost:5173"])
    environment: Literal["development", "staging", "production"] = "development"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_redis_url: str | None = None

    # AI Controls
    ai_max_calls_per_move: int = 5
    ai_max_calls_per_game: int = 200
    ai_daily_game_limit: int = 50
    ai_cache_ttl: int = 300

    # Monitoring
    sentry_dsn: str | None = None
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "case_sensitive": False}

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: SecretStr, info) -> SecretStr:
        """Validate secret key meets security requirements in production."""
        if info.data.get("environment") == "production":
            secret = v.get_secret_value()
            if len(secret) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
            if secret == "dev-secret-key-change-in-production":
                raise ValueError("Must set custom SECRET_KEY in production")
        return v

    @field_validator("allowed_origins")
    @classmethod
    def validate_cors(cls, v: list[str], info) -> list[str]:
        """Ensure CORS is not wildcard in production."""
        if info.data.get("environment") == "production":
            if "*" in v:
                raise ValueError("Cannot use wildcard CORS origins in production")
        return v

    @field_validator("supabase_url")
    @classmethod
    def validate_supabase(cls, v: str, info) -> str:
        """Ensure Supabase URL is configured in staging/production."""
        if info.data.get("environment") in ["staging", "production"]:
            if "placeholder" in v:
                raise ValueError("SUPABASE_URL required in staging/production")
        return v


settings = Settings()
