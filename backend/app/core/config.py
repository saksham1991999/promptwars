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
    posthog_api_key: str | None = None
    posthog_host: str = "https://app.posthog.com"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
