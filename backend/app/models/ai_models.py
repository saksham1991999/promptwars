"""AI-related Pydantic models for agent I/O."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Piece Response Agent
# ---------------------------------------------------------------------------

class PieceResponseInput(BaseModel):
    piece_type: str
    personality: dict
    morale: int = Field(ge=0, le=100)
    move_command: str
    target_square: str
    board_context: str
    is_risky: bool
    capture_target: str | None = None


class PieceResponseOutput(BaseModel):
    will_move: bool
    response_text: str
    morale_change: int = Field(ge=-15, le=15)
    reason_for_refusal: str | None = None
    suggested_alternative: str | None = None


# ---------------------------------------------------------------------------
# Analysis Agent
# ---------------------------------------------------------------------------

class MoveAnalysisInput(BaseModel):
    fen_before: str
    fen_after: str
    move_san: str
    move_number: int
    material_balance: int


class MoveAnalysisOutput(BaseModel):
    move_quality: int = Field(ge=1, le=10)
    evaluation: float
    threats: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    analysis_text: str
    morale_impact: dict[str, int] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Persuasion Agent
# ---------------------------------------------------------------------------

class PersuasionInput(BaseModel):
    piece_type: str
    personality: dict
    morale: int
    player_argument: str
    move_description: str
    board_analysis: str
    is_claim_accurate: bool
    trust_history: float = Field(ge=0, le=1, default=0.5)


class PersuasionOutput(BaseModel):
    is_persuaded: bool
    response_text: str
    logic_score: int = Field(ge=0, le=25)
    personality_match: int = Field(ge=0, le=15)
    final_probability: float
    reasoning: str


# ---------------------------------------------------------------------------
# Taunt Generator
# ---------------------------------------------------------------------------

class TauntInput(BaseModel):
    game_state: str
    trigger_event: str
    material_balance: int
    move_count: int


class TauntOutput(BaseModel):
    taunt_text: str
    intensity: int = Field(ge=1, le=5)


# ---------------------------------------------------------------------------
# Custom Piece Creator
# ---------------------------------------------------------------------------

class CustomPieceInput(BaseModel):
    piece_type: str
    user_prompt: str
    color: str


class CustomPieceOutput(BaseModel):
    archetype: str
    traits: list[str]
    dialogue_style: str
    sample_dialogues: list[str]
    morale_modifiers: dict[str, int]
    visual_description: str
