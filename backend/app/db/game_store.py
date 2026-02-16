"""In-memory game store — replaces Supabase DB for anonymous gameplay.

Stores games, pieces, chat messages, moves, and persuasion attempts in
Python dicts.  Data is lost on server restart — fine for dev/demo.
"""

from __future__ import annotations

import random
import string
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import chess


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid4())


def _share_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


# Default piece personalities
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


class InMemoryGameStore:
    """Thread-safe-enough in-memory store for game state."""

    def __init__(self) -> None:
        self.games: dict[str, dict[str, Any]] = {}
        self.pieces: dict[str, dict[str, Any]] = {}  # piece_id -> piece
        self.messages: dict[str, list[dict[str, Any]]] = {}  # game_id -> [msgs]
        self.moves: dict[str, list[dict[str, Any]]] = {}  # game_id -> [moves]
        self.persuasions: dict[str, list[dict[str, Any]]] = {}

        # Performance indexes
        self._share_code_index: dict[str, str] = {}  # share_code -> game_id (O(1) lookup)
        self._pieces_by_game: dict[str, list[str]] = {}  # game_id -> [piece_ids]
        self._pieces_by_square: dict[tuple[str, str], str] = {}  # (game_id, square) -> piece_id
    
    async def health_check(self) -> bool:
        """Verify the store is healthy (always true for in-memory)."""
        return True

    # ---- Games ----

    def create_game(
        self,
        session_id: str,
        game_mode: str = "pvai",
        template: str = "classic",
        settings: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        game_id = _new_id()
        share_code = _share_code()
        game: dict[str, Any] = {
            "id": game_id,
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
            "created_at": _now_iso(),
        }
        self.games[game_id] = game
        self.messages[game_id] = []
        self.moves[game_id] = []
        self.persuasions[game_id] = []

        # Update indexes
        self._share_code_index[share_code] = game_id
        self._pieces_by_game[game_id] = []

        # Create pieces
        for p in STARTING_PIECES:
            pid = _new_id()
            personality = DEFAULT_PERSONALITIES.get(p["piece_type"], DEFAULT_PERSONALITIES["pawn"])
            piece = {
                "id": pid,
                "game_id": game_id,
                "color": p["color"],
                "piece_type": p["piece_type"],
                "square": p["square"],
                "morale": 70,
                "personality": personality,
                "is_captured": False,
                "created_at": _now_iso(),
            }
            self.pieces[pid] = piece
            # Update indexes
            self._pieces_by_game[game_id].append(pid)
            self._pieces_by_square[(game_id, p["square"])] = pid

        # System message
        self.add_message(game_id, "system", "System", f"Game created! Mode: {game_mode}. Template: {template}.")

        return game

    def get_game(self, game_id: str) -> dict[str, Any] | None:
        return self.games.get(game_id)

    def get_game_by_share_code(self, code: str) -> dict[str, Any] | None:
        """Get game by share code - O(1) using hash index."""
        game_id = self._share_code_index.get(code)
        if game_id:
            return self.games.get(game_id)
        return None

    def update_game(self, game_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        game = self.games.get(game_id)
        if game:
            game.update(data)
        return game

    # ---- Pieces ----

    def get_game_pieces(self, game_id: str) -> list[dict[str, Any]]:
        """Get all pieces for a game - O(1) using hash index."""
        piece_ids = self._pieces_by_game.get(game_id, [])
        return [self.pieces[pid] for pid in piece_ids if pid in self.pieces]

    def get_piece(self, piece_id: str) -> dict[str, Any] | None:
        return self.pieces.get(piece_id)

    def update_piece(self, piece_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update piece and maintain square index."""
        piece = self.pieces.get(piece_id)
        if piece:
            # Update square index if square changed
            if "square" in data and data["square"] != piece.get("square"):
                old_square = piece.get("square")
                new_square = data["square"]
                game_id = piece["game_id"]

                # Remove old index
                if old_square:
                    self._pieces_by_square.pop((game_id, old_square), None)

                # Add new index (if not captured)
                if new_square and not data.get("is_captured", piece.get("is_captured")):
                    self._pieces_by_square[(game_id, new_square)] = piece_id

            # If piece is captured, remove from square index
            if data.get("is_captured") and not piece.get("is_captured"):
                game_id = piece["game_id"]
                square = piece.get("square")
                if square:
                    self._pieces_by_square.pop((game_id, square), None)

            piece.update(data)
        return piece

    def get_piece_at_square(self, game_id: str, square: str) -> dict[str, Any] | None:
        """Get piece at a specific square - O(1) using hash index."""
        piece_id = self._pieces_by_square.get((game_id, square))
        if piece_id:
            return self.pieces.get(piece_id)
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
        msg = {
            "id": _new_id(),
            "game_id": game_id,
            "sender_id": sender_id,
            "message_type": message_type,
            "sender_name": sender_name,
            "content": content,
            "metadata": metadata or {},
            "created_at": _now_iso(),
        }
        self.messages.setdefault(game_id, []).append(msg)
        return msg

    def get_messages(self, game_id: str, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        msgs = self.messages.get(game_id, [])
        return msgs[offset : offset + limit]

    def get_message_count(self, game_id: str) -> int:
        return len(self.messages.get(game_id, []))

    # ---- Moves ----

    def add_move(self, game_id: str, data: dict[str, Any]) -> dict[str, Any]:
        move = {"id": _new_id(), **data, "created_at": _now_iso()}
        self.moves.setdefault(game_id, []).append(move)
        return move

    def get_moves(self, game_id: str) -> list[dict[str, Any]]:
        return self.moves.get(game_id, [])

    def get_move_count(self, game_id: str) -> int:
        return len(self.moves.get(game_id, []))

    # ---- Persuasion ----

    def add_persuasion(self, game_id: str, data: dict[str, Any]) -> dict[str, Any]:
        record = {"id": _new_id(), **data, "created_at": _now_iso()}
        self.persuasions.setdefault(game_id, []).append(record)
        return record


# Singleton
store = InMemoryGameStore()
