"""Supabase game store — persistent database storage for production.

Replaces InMemoryGameStore with actual Supabase PostgreSQL operations.
All game state persists across server restarts.
"""

from __future__ import annotations

import logging
import secrets
import string
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import chess
from supabase import Client, create_client

from app.core.config import settings

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    """Generate a new UUID string."""
    return str(uuid4())


def _secure_share_code() -> str:
    """Generate a cryptographically secure 6-character share code."""
    return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))


# Default piece personalities (same as in-memory store)
DEFAULT_PERSONALITIES: dict[str, dict[str, Any]] = {
    "pawn": {"archetype": "Naive Recruit", "traits": ["eager", "nervous", "loyal"], "dialogue_style": "Enthusiastic, anxious"},
    "knight": {"archetype": "Cocky Maverick", "traits": ["boastful", "adventurous", "impatient"], "dialogue_style": "Confident, dramatic"},
    "bishop": {"archetype": "Intellectual Strategist", "traits": ["analytical", "cautious", "eloquent"], "dialogue_style": "Measured, logical"},
    "rook": {"archetype": "Loyal Soldier", "traits": ["disciplined", "stoic", "reliable"], "dialogue_style": "Military, direct"},
    "queen": {"archetype": "Confident Diva", "traits": ["commanding", "dramatic", "self-assured"], "dialogue_style": "Regal, demanding"},
    "king": {"archetype": "Nervous Leader", "traits": ["anxious", "grateful", "commanding"], "dialogue_style": "Worried, authoritative"},
}

STARTING_PIECES = [
    {"color": "white", "piece_type": "rook", "square": "a1"},
    {"color": "white", "piece_type": "knight", "square": "b1"},
    {"color": "white", "piece_type": "bishop", "square": "c1"},
    {"color": "white", "piece_type": "queen", "square": "d1"},
    {"color": "white", "piece_type": "king", "square": "e1"},
    {"color": "white", "piece_type": "bishop", "square": "f1"},
    {"color": "white", "piece_type": "knight", "square": "g1"},
    {"color": "white", "piece_type": "rook", "square": "h1"},
    *[{"color": "white", "piece_type": "pawn", "square": f"{f}2"} for f in "abcdefgh"],
    {"color": "black", "piece_type": "rook", "square": "a8"},
    {"color": "black", "piece_type": "knight", "square": "b8"},
    {"color": "black", "piece_type": "bishop", "square": "c8"},
    {"color": "black", "piece_type": "queen", "square": "d8"},
    {"color": "black", "piece_type": "king", "square": "e8"},
    {"color": "black", "piece_type": "bishop", "square": "f8"},
    {"color": "black", "piece_type": "knight", "square": "g8"},
    {"color": "black", "piece_type": "rook", "square": "h8"},
    *[{"color": "black", "piece_type": "pawn", "square": f"{f}7"} for f in "abcdefgh"],
]


class SupabaseGameStore:
    """Production-ready game store using Supabase PostgreSQL."""

    def __init__(self) -> None:
        """Initialize Supabase client with connection pooling."""
        try:
            self.client: Client = create_client(
                settings.supabase_url,
                settings.supabase_secret_key.get_secret_value(),
            )
            logger.info("Supabase game store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
            raise

    async def health_check(self) -> bool:
        """Health check - verify database connectivity."""
        try:
            result = self.client.table("games").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}", exc_info=True)
            return False

    # ---- Games ----

    def create_game(
        self,
        session_id: str,
        game_mode: str = "pvai",
        template: str = "classic",
        settings: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new game with initial pieces.

        Args:
            session_id: Player session identifier
            game_mode: 'pvai' or 'pvp'
            template: Game template name
            settings: Game settings (timer, surprise mode, etc.)

        Returns:
            Game dict with id, status, share_code, etc.
        """
        try:
            share_code = _secure_share_code()
            game_data = {
                "status": "active" if game_mode == "pvai" else "waiting",
                "game_mode": game_mode,
                "template": template,
                "share_code": share_code,
                "fen": chess.STARTING_FEN,
                "turn": "white",
                "white_player_id": session_id,
                "black_player_id": "ai" if game_mode == "pvai" else None,
                "result": None,
                "settings": settings or {"surprise_mode": False, "turn_timer": None, "ai_difficulty": "medium"},
            }

            # Insert game
            result = self.client.table("games").insert(game_data).execute()
            if not result.data:
                raise ValueError("Game creation failed - no data returned")

            game = result.data[0]
            game_id = game["id"]

            # Create all 32 starting pieces
            pieces_data = []
            for p in STARTING_PIECES:
                personality = DEFAULT_PERSONALITIES.get(p["piece_type"], DEFAULT_PERSONALITIES["pawn"])
                pieces_data.append({
                    "game_id": game_id,
                    "color": p["color"],
                    "piece_type": p["piece_type"],
                    "square": p["square"],
                    "morale": 70,
                    "personality": personality,
                    "is_captured": False,
                })

            self.client.table("game_pieces").insert(pieces_data).execute()

            # Add system message
            self.add_message(
                game_id,
                "system",
                "System",
                f"Game created! Mode: {game_mode}. Template: {template}.",
            )

            logger.info(f"Created game {game_id} with share code {share_code}")
            return game

        except Exception as e:
            logger.error(f"Failed to create game: {e}", exc_info=True)
            raise

    def get_game(self, game_id: str) -> dict[str, Any] | None:
        """Get game by ID."""
        try:
            result = self.client.table("games").select("*").eq("id", game_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get game {game_id}: {e}", exc_info=True)
            return None

    def get_game_by_share_code(self, code: str) -> dict[str, Any] | None:
        """Get game by share code."""
        try:
            result = self.client.table("games").select("*").eq("share_code", code).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get game by share code {code}: {e}", exc_info=True)
            return None

    def update_game(self, game_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update game fields."""
        try:
            result = self.client.table("games").update(data).eq("id", game_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to update game {game_id}: {e}", exc_info=True)
            return None

    # ---- Pieces ----

    def get_game_pieces(self, game_id: str) -> list[dict[str, Any]]:
        """Get all pieces for a game."""
        try:
            result = self.client.table("game_pieces").select("*").eq("game_id", game_id).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get pieces for game {game_id}: {e}", exc_info=True)
            return []

    def get_piece(self, piece_id: str) -> dict[str, Any] | None:
        """Get a single piece by ID."""
        try:
            result = self.client.table("game_pieces").select("*").eq("id", piece_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get piece {piece_id}: {e}", exc_info=True)
            return None

    def update_piece(self, piece_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update piece fields (morale, square, is_captured, etc.)."""
        try:
            result = self.client.table("game_pieces").update(data).eq("id", piece_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to update piece {piece_id}: {e}", exc_info=True)
            return None

    def get_piece_at_square(self, game_id: str, square: str) -> dict[str, Any] | None:
        """Get the piece at a specific square (if not captured)."""
        try:
            result = (
                self.client.table("game_pieces")
                .select("*")
                .eq("game_id", game_id)
                .eq("square", square)
                .eq("is_captured", False)
                .execute()
            )
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get piece at {square} in game {game_id}: {e}", exc_info=True)
            return None

    # ---- Chat Messages ----

    def add_message(
        self,
        game_id: str,
        message_type: str,
        sender_name: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        sender_id: str | None = None,
    ) -> dict[str, Any]:
        """Add a chat message to a game."""
        try:
            message_data = {
                "game_id": game_id,
                "sender_id": sender_id,
                "message_type": message_type,
                "sender_name": sender_name,
                "content": content,
                "metadata": metadata or {},
            }
            result = self.client.table("chat_messages").insert(message_data).execute()
            if result.data:
                return result.data[0]
            raise ValueError("Message creation failed - no data returned")
        except Exception as e:
            logger.error(f"Failed to add message to game {game_id}: {e}", exc_info=True)
            raise

    def get_messages(self, game_id: str, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """Get paginated chat messages for a game."""
        try:
            result = (
                self.client.table("chat_messages")
                .select("*")
                .eq("game_id", game_id)
                .order("created_at", desc=False)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get messages for game {game_id}: {e}", exc_info=True)
            return []

    def get_message_count(self, game_id: str) -> int:
        """Get total message count for a game."""
        try:
            result = (
                self.client.table("chat_messages")
                .select("id", count="exact")
                .eq("game_id", game_id)
                .execute()
            )
            return result.count if result.count is not None else 0
        except Exception as e:
            logger.error(f"Failed to get message count for game {game_id}: {e}", exc_info=True)
            return 0

    # ---- Moves ----

    def add_move(self, game_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Record a move in the game."""
        try:
            move_data = {"game_id": game_id, **data}
            result = self.client.table("game_moves").insert(move_data).execute()
            if result.data:
                return result.data[0]
            raise ValueError("Move creation failed - no data returned")
        except Exception as e:
            logger.error(f"Failed to add move to game {game_id}: {e}", exc_info=True)
            raise

    def get_moves(self, game_id: str) -> list[dict[str, Any]]:
        """Get all moves for a game."""
        try:
            result = (
                self.client.table("game_moves")
                .select("*")
                .eq("game_id", game_id)
                .order("created_at", desc=False)
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get moves for game {game_id}: {e}", exc_info=True)
            return []

    def get_move_count(self, game_id: str) -> int:
        """Get total move count for a game."""
        try:
            result = (
                self.client.table("game_moves")
                .select("id", count="exact")
                .eq("game_id", game_id)
                .execute()
            )
            return result.count if result.count is not None else 0
        except Exception as e:
            logger.error(f"Failed to get move count for game {game_id}: {e}", exc_info=True)
            return 0

    # ---- Persuasion ----

    def add_persuasion(self, game_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Record a persuasion attempt."""
        try:
            persuasion_data = {"game_id": game_id, **data}
            result = self.client.table("persuasion_attempts").insert(persuasion_data).execute()
            if result.data:
                return result.data[0]
            raise ValueError("Persuasion record creation failed - no data returned")
        except Exception as e:
            logger.error(f"Failed to add persuasion to game {game_id}: {e}", exc_info=True)
            raise


# Singleton instance
store = SupabaseGameStore()
