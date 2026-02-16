"""Game-related Pydantic request/response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared / Common Models
# ---------------------------------------------------------------------------


class PlayerSummary(BaseModel):
    id: str
    username: str
    avatar_url: str | None = None


class PiecePersonality(BaseModel):
    archetype: str = "default"
    traits: list[str] = Field(default_factory=list)
    dialogue_style: str = "neutral"
    custom_prompt: str = ""
    morale_modifiers: dict[str, int] = Field(default_factory=dict)


class PieceState(BaseModel):
    id: str
    color: str
    piece_type: str
    square: str | None = None
    morale: int = 70
    personality: PiecePersonality = Field(default_factory=PiecePersonality)
    is_captured: bool = False


class MoveData(BaseModel):
    from_square: str
    to_square: str
    san: str
    piece_type: str


class BoardState(BaseModel):
    fen: str
    turn: str
    is_check: bool = False
    is_checkmate: bool = False
    is_stalemate: bool = False
    last_move: MoveData | None = None


class MoraleChange(BaseModel):
    piece_id: str
    event_type: str
    change: int
    morale_after: int
    description: str


class GameSettings(BaseModel):
    surprise_mode: bool = False
    turn_timer: int | None = None
    ai_difficulty: Literal["easy", "medium", "hard"] = "medium"


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------


class CreateGameRequest(BaseModel):
    game_mode: Literal["pvp", "pvai"] = "pvp"
    template: Literal[
        "classic", "power_chess", "leaper_madness", "hopper_havoc", "pawn_revolution"
    ] = "classic"
    settings: GameSettings | None = None


class JoinGameRequest(BaseModel):
    share_code: str


class CommandRequest(BaseModel):
    piece_id: str
    target_square: str
    message: str | None = None


class PersuasionRequest(BaseModel):
    piece_id: str
    target_square: str
    argument: str
    is_voice: bool = False


class ResignRequest(BaseModel):
    pass


class DrawOfferRequest(BaseModel):
    pass


class DrawRespondRequest(BaseModel):
    accept: bool


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------


class PieceResponseData(BaseModel):
    will_move: bool
    response_text: str
    morale_before: int
    morale_after: int
    reason_for_refusal: str | None = None


class MoveAnalysis(BaseModel):
    move_quality: int = Field(ge=1, le=10)
    evaluation: float
    threats: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    analysis_text: str = ""


class CommandResponse(BaseModel):
    success: bool
    move_executed: bool
    piece_response: PieceResponseData
    board_state: BoardState
    morale_changes: list[MoraleChange] = Field(default_factory=list)
    analysis: MoveAnalysis | None = None
    king_taunt: str | None = None


class PersuasionEvaluation(BaseModel):
    logic_score: int = Field(ge=0, le=25)
    personality_match: int = Field(ge=0, le=15)
    morale_modifier: int = Field(ge=-20, le=20)
    trust_modifier: int = Field(ge=-15, le=10)
    urgency_factor: int = Field(ge=0, le=10)
    total_probability: float


class PersuasionResponse(BaseModel):
    success: bool
    probability: float
    piece_response: str
    move_executed: bool
    board_state: BoardState | None = None
    evaluation: PersuasionEvaluation


class GameResponse(BaseModel):
    id: str
    status: str
    game_mode: str
    template: str
    share_code: str
    fen: str
    turn: str
    white_player: PlayerSummary | None = None
    black_player: PlayerSummary | None = None
    pieces: list[PieceState] = Field(default_factory=list)
    settings: GameSettings = Field(default_factory=GameSettings)
    created_at: datetime


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict | None = None
