"""Test fixtures and utilities for Chess Alive backend tests."""

from .data import STANDARD_FEN, MIDDLEGAME_FEN, ENDGAME_FEN, CHECKMATE_FEN, STALEMATE_FEN
from .factories import (
    ProfileFactory,
    GameFactory,
    GamePieceFactory,
    GameMoveFactory,
    ChatMessageFactory,
    PersuasionAttemptFactory,
    MoraleEventFactory,
)

__all__ = [
    "STANDARD_FEN",
    "MIDDLEGAME_FEN",
    "ENDGAME_FEN",
    "CHECKMATE_FEN",
    "STALEMATE_FEN",
    "ProfileFactory",
    "GameFactory",
    "GamePieceFactory",
    "GameMoveFactory",
    "ChatMessageFactory",
    "PersuasionAttemptFactory",
    "MoraleEventFactory",
]