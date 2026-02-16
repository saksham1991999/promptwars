"""Shared FastAPI dependencies for game validation and session management."""

from __future__ import annotations

from uuid import uuid4

from fastapi import Header, HTTPException, status

from app.db import store


def get_session_id(x_session_id: str | None = Header(None)) -> str:
    """
    Extract or create session ID from header.

    Args:
        x_session_id: Optional session ID from X-Session-Id header

    Returns:
        Session ID (existing or newly generated)
    """
    return x_session_id or str(uuid4())


def get_active_game(game_id: str) -> dict:
    """
    Get game and raise 404 if not found or not active.

    This dependency eliminates the 11+ duplicated game validation patterns
    across routers.

    Args:
        game_id: Game identifier

    Returns:
        Game dict from store

    Raises:
        HTTPException: 404 if game not found, 400 if not active
    """
    game = store.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "GAME_NOT_FOUND",
                "message": "Game not found",
            },
        )
    if game["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "GAME_NOT_ACTIVE",
                "message": f"Game is {game['status']}, not active",
            },
        )
    return game


def get_game_or_404(game_id: str) -> dict:
    """
    Get game and raise 404 if not found (any status).

    For endpoints that need to access games regardless of status
    (e.g., viewing completed games).

    Args:
        game_id: Game identifier

    Returns:
        Game dict from store

    Raises:
        HTTPException: 404 if game not found
    """
    game = store.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "GAME_NOT_FOUND",
                "message": "Game not found",
            },
        )
    return game
