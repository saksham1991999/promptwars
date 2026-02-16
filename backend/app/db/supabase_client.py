"""Supabase client initialization and connection management."""

from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Get or create the Supabase client singleton (secret key / service role)."""
    return create_client(settings.supabase_url, settings.supabase_secret_key.get_secret_value())


@lru_cache(maxsize=1)
def get_supabase_anon_client() -> Client:
    """Get or create the Supabase client singleton (publishable key, for auth)."""
    return create_client(settings.supabase_url, settings.supabase_publishable_key)
