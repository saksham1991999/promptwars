"""Test fixtures for PromptWars backend tests."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.db.game_store import InMemoryGameStore
from app.main import app
from app.models.ai_models import PieceResponseOutput


@pytest.fixture
def client() -> TestClient:
    """
    FastAPI test client.

    Returns:
        TestClient instance for making API requests
    """
    return TestClient(app)


@pytest.fixture
def game_store() -> InMemoryGameStore:
    """
    Fresh in-memory game store for each test.

    Returns:
        Clean InMemoryGameStore instance

    Yields:
        Game store
    """
    store = InMemoryGameStore()
    yield store
    # Cleanup after test
    store._games.clear()
    store._pieces.clear()
    store._moves.clear()
    store._messages.clear()


@pytest.fixture
def sample_game_data() -> dict:
    """
    Sample game data for testing.

    Returns:
        Dict with game data matching InMemoryGameStore format
    """
    game_id = str(uuid4())
    session_id = str(uuid4())

    return {
        "id": game_id,
        "white_player_id": session_id,
        "black_player_id": "ai",
        "status": "active",
        "game_mode": "pvai",
        "template": "classic",
        "share_code": "ABC123",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "pgn": "",
        "turn": "white",
        "result": None,
        "settings": {
            "surprise_mode": False,
            "turn_timer": None,
            "ai_difficulty": "medium",
        },
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "session_id": session_id,
    }


@pytest.fixture
def sample_piece_data() -> dict:
    """
    Sample chess piece data for testing.

    Returns:
        Dict with piece data matching InMemoryGameStore format
    """
    return {
        "id": str(uuid4()),
        "game_id": str(uuid4()),
        "color": "white",
        "piece_type": "pawn",
        "square": "e2",
        "morale": 70,
        "personality": {
            "archetype": "default",
            "traits": [],
            "dialogue_style": "neutral",
            "custom_prompt": "",
            "morale_modifiers": {},
        },
        "is_captured": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def mock_gemini_service(monkeypatch):
    """
    Mock Gemini AI service to avoid API calls in tests.

    This fixture patches all AI service methods to return
    predictable test data instead of making real API calls.

    Args:
        monkeypatch: pytest monkeypatch fixture

    Returns:
        Mock response data for verification
    """
    from app.services import gemini_service

    # Mock piece response
    async def mock_get_piece_response(*args, **kwargs):
        return PieceResponseOutput(
            will_move=True,
            response_text="Test response from mock AI",
            morale_change=5,
        )

    # Mock analysis
    async def mock_get_move_analysis(*args, **kwargs):
        return {
            "move_quality": 7,
            "evaluation": 0.5,
            "threats": ["e4 pawn vulnerable"],
            "opportunities": ["control center"],
            "analysis_text": "Solid opening move",
        }

    # Mock persuasion evaluation
    async def mock_evaluate_persuasion(*args, **kwargs):
        return {
            "logic_score": 15,
            "personality_match": 10,
            "morale_modifier": 5,
            "trust_modifier": 0,
            "urgency_factor": 5,
            "total_probability": 0.65,
            "explanation": "Mock persuasion evaluation",
        }

    # Mock king taunt
    async def mock_get_king_taunt(*args, **kwargs):
        return "Mock king taunt"

    # Apply mocks
    monkeypatch.setattr(
        gemini_service.GeminiService, "get_piece_response", mock_get_piece_response
    )
    monkeypatch.setattr(
        gemini_service.GeminiService, "get_move_analysis", mock_get_move_analysis
    )
    monkeypatch.setattr(
        gemini_service.GeminiService,
        "evaluate_persuasion",
        mock_evaluate_persuasion,
    )
    monkeypatch.setattr(
        gemini_service.GeminiService, "get_king_taunt", mock_get_king_taunt
    )

    return {
        "piece_response": mock_get_piece_response,
        "analysis": mock_get_move_analysis,
        "persuasion": mock_evaluate_persuasion,
        "taunt": mock_get_king_taunt,
    }


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """
    Auth headers for authenticated requests.

    Returns:
        Dict with X-Session-Id header
    """
    return {"X-Session-Id": str(uuid4())}


@pytest.fixture
def sample_chess_position() -> dict:
    """
    Sample chess position for testing move validation.

    Returns:
        Dict with FEN and expected legal moves
    """
    return {
        "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "last_move": {"from": "e2", "to": "e4"},
        "legal_moves_for_e7_pawn": ["e5", "e6"],
    }
