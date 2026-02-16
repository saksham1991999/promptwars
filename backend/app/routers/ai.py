"""AI router — custom piece generation and analysis endpoints."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])


class CustomPieceRequest(BaseModel):
    piece_type: str
    prompt: str
    color: str = "white"


@router.post("/custom-piece")
async def generate_custom_piece(
    request: CustomPieceRequest,
    user: dict[str, Any] = Depends(get_current_user),
):
    """Generate a custom piece personality using AI."""
    from app.services.gemini_service import gemini_service

    try:
        result = await gemini_service.create_custom_piece(
            piece_type=request.piece_type,
            user_prompt=request.prompt,
            color=request.color,
        )
        return {
            "personality": {
                "archetype": result.archetype,
                "traits": result.traits,
                "dialogue_style": result.dialogue_style,
                "morale_modifiers": result.morale_modifiers,
            },
            "preview_dialogue": result.sample_dialogues,
            "visual_description": result.visual_description,
        }
    except Exception as exc:
        logger.error("Custom piece generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error_code": "AI_SERVICE_ERROR", "message": "AI service unavailable"},
        ) from exc


@router.get("/games/{game_id}/analysis")
async def get_latest_analysis(
    game_id: str,
    user: dict[str, Any] = Depends(get_current_user),
):
    """Get the latest AI analysis for a game."""
    from app.db import queries

    messages = queries.get_chat_messages(game_id, limit=10)
    analysis_messages = [m for m in messages if m.get("message_type") == "ai_analysis"]

    if not analysis_messages:
        return {"analysis": None}

    latest = analysis_messages[-1]
    return {
        "analysis": {
            "content": latest["content"],
            "metadata": latest.get("metadata", {}),
            "created_at": latest.get("created_at"),
        }
    }
