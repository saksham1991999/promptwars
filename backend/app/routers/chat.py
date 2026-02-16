"""Chat router — chat history and message sending (Supabase store)."""

from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Query

from app.db import store
from app.models.chat_models import SendMessageRequest

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


@router.get("/games/{game_id}/chat")
async def get_chat_history(
    game_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
):
    """Get paginated chat history for a game."""
    game = store.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail={"error_code": "GAME_NOT_FOUND", "message": "Game not found"})

    offset = (page - 1) * page_size
    messages = store.get_messages(game_id, limit=page_size, offset=offset)
    total = store.get_message_count(game_id)

    return {
        "data": messages,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": offset + page_size < total,
    }


@router.post("/games/{game_id}/chat")
async def send_message(
    game_id: str,
    request: SendMessageRequest,
    x_session_id: str | None = Header(default=None),
):
    """Send a player message in game chat."""
    session_id = x_session_id or str(uuid4())

    game = store.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail={"error_code": "GAME_NOT_FOUND", "message": "Game not found"})

    sender_name = f"Player-{session_id[:6]}"

    message = store.add_message(
        game_id=game_id,
        message_type=request.message_type,
        sender_name=sender_name,
        content=request.content,
        sender_id=session_id,
    )

    return message
