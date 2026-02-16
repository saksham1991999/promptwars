"""Database query functions for all tables."""

from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------


def get_profile(user_id: str) -> dict[str, Any] | None:
    """Fetch a user profile by ID."""
    client = get_supabase_client()
    result = client.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
    return result.data


def update_profile(user_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update a user profile."""
    client = get_supabase_client()
    result = client.table("profiles").update(data).eq("id", user_id).execute()
    return result.data[0] if result.data else None


# ---------------------------------------------------------------------------
# Games
# ---------------------------------------------------------------------------


def create_game(data: dict[str, Any]) -> dict[str, Any]:
    """Create a new game."""
    client = get_supabase_client()
    result = client.table("games").insert(data).execute()
    return result.data[0]


def get_game(game_id: str) -> dict[str, Any] | None:
    """Get a game by ID."""
    client = get_supabase_client()
    result = client.table("games").select("*").eq("id", game_id).maybe_single().execute()
    return result.data


def get_game_by_share_code(share_code: str) -> dict[str, Any] | None:
    """Get a game by share code."""
    client = get_supabase_client()
    result = (
        client.table("games")
        .select("*")
        .eq("share_code", share_code)
        .maybe_single()
        .execute()
    )
    return result.data


def update_game(game_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update a game."""
    client = get_supabase_client()
    result = client.table("games").update(data).eq("id", game_id).execute()
    return result.data[0] if result.data else None


def get_user_games(user_id: str, limit: int = 20) -> list[dict[str, Any]]:
    """Get recent games for a user."""
    client = get_supabase_client()
    result = (
        client.table("games")
        .select("*")
        .or_(f"white_player_id.eq.{user_id},black_player_id.eq.{user_id}")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


# ---------------------------------------------------------------------------
# Game Pieces
# ---------------------------------------------------------------------------


def create_game_pieces(pieces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Insert all pieces for a game."""
    client = get_supabase_client()
    result = client.table("game_pieces").insert(pieces).execute()
    return result.data or []


def get_game_pieces(game_id: str) -> list[dict[str, Any]]:
    """Get all pieces for a game."""
    client = get_supabase_client()
    result = client.table("game_pieces").select("*").eq("game_id", game_id).execute()
    return result.data or []


def get_piece(piece_id: str) -> dict[str, Any] | None:
    """Get a single piece by ID."""
    client = get_supabase_client()
    result = client.table("game_pieces").select("*").eq("id", piece_id).maybe_single().execute()
    return result.data


def update_piece(piece_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update a game piece."""
    client = get_supabase_client()
    result = client.table("game_pieces").update(data).eq("id", piece_id).execute()
    return result.data[0] if result.data else None


def get_piece_by_square(game_id: str, square: str, color: str) -> dict[str, Any] | None:
    """Find a piece at a specific square."""
    client = get_supabase_client()
    result = (
        client.table("game_pieces")
        .select("*")
        .eq("game_id", game_id)
        .eq("square", square)
        .eq("color", color)
        .eq("is_captured", False)
        .maybe_single()
        .execute()
    )
    return result.data


# ---------------------------------------------------------------------------
# Game Moves
# ---------------------------------------------------------------------------


def create_move(data: dict[str, Any]) -> dict[str, Any]:
    """Record a game move."""
    client = get_supabase_client()
    result = client.table("game_moves").insert(data).execute()
    return result.data[0]


def get_game_moves(game_id: str) -> list[dict[str, Any]]:
    """Get all moves for a game, ordered."""
    client = get_supabase_client()
    result = (
        client.table("game_moves")
        .select("*")
        .eq("game_id", game_id)
        .order("move_number")
        .execute()
    )
    return result.data or []


def get_move_count(game_id: str) -> int:
    """Get the current move count for a game."""
    client = get_supabase_client()
    result = (
        client.table("game_moves")
        .select("id", count="exact")
        .eq("game_id", game_id)
        .execute()
    )
    return result.count or 0


# ---------------------------------------------------------------------------
# Chat Messages
# ---------------------------------------------------------------------------


def create_chat_message(data: dict[str, Any]) -> dict[str, Any]:
    """Insert a chat message."""
    client = get_supabase_client()
    result = client.table("chat_messages").insert(data).execute()
    return result.data[0]


def get_chat_messages(
    game_id: str, limit: int = 50, offset: int = 0
) -> list[dict[str, Any]]:
    """Get paginated chat messages for a game."""
    client = get_supabase_client()
    result = (
        client.table("chat_messages")
        .select("*")
        .eq("game_id", game_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return list(reversed(result.data or []))


def get_chat_count(game_id: str) -> int:
    """Get total chat message count for a game."""
    client = get_supabase_client()
    result = (
        client.table("chat_messages")
        .select("id", count="exact")
        .eq("game_id", game_id)
        .execute()
    )
    return result.count or 0


# ---------------------------------------------------------------------------
# Persuasion Attempts
# ---------------------------------------------------------------------------


def create_persuasion_attempt(data: dict[str, Any]) -> dict[str, Any]:
    """Record a persuasion attempt."""
    client = get_supabase_client()
    result = client.table("persuasion_attempts").insert(data).execute()
    return result.data[0]


def get_persuasion_history(game_id: str, piece_id: str) -> list[dict[str, Any]]:
    """Get persuasion attempts for a specific piece in a game."""
    client = get_supabase_client()
    result = (
        client.table("persuasion_attempts")
        .select("*")
        .eq("game_id", game_id)
        .eq("piece_id", piece_id)
        .order("created_at")
        .execute()
    )
    return result.data or []


# ---------------------------------------------------------------------------
# Morale Events
# ---------------------------------------------------------------------------


def create_morale_event(data: dict[str, Any]) -> dict[str, Any]:
    """Record a morale change event."""
    client = get_supabase_client()
    result = client.table("morale_events").insert(data).execute()
    return result.data[0]


def get_morale_events(piece_id: str) -> list[dict[str, Any]]:
    """Get morale history for a piece."""
    client = get_supabase_client()
    result = (
        client.table("morale_events")
        .select("*")
        .eq("piece_id", piece_id)
        .order("created_at")
        .execute()
    )
    return result.data or []
