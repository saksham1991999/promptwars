"""Chat message Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ChatMessage(BaseModel):
    id: str
    message_type: str
    sender_name: str
    content: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime


class SendMessageRequest(BaseModel):
    content: str = Field(max_length=1000)
    message_type: str = "player_message"


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    page: int
    page_size: int
    has_more: bool
