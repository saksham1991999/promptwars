"""Test fixtures for Chess Alive backend tests."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Generator
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.db.game_store import InMemoryGameStore
from app.main import app
from app.models.ai_models import PieceResponseOutput

# Import fixtures data and factories
from tests.fixtures.data import (
    STANDARD_FEN,
    SAMPLE_PIECE_IDS,
    MORALE_CHANGES,
)
from tests.fixtures.factories import (
    ProfileFactory,
    GameFactory,
    GamePieceFactory,
    GameMoveFactory,
    ChatMessageFactory,
    PersuasionAttemptFactory,
    MoraleEventFactory,
)


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
    store.games.clear()
    store.pieces.clear()
    store.moves.clear()
    store.messages.clear()


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


# ============================================================================
# Factory Fixtures
# ============================================================================

@pytest.fixture
def profile_factory() -> type[ProfileFactory]:
    """Return ProfileFactory class."""
    return ProfileFactory


@pytest.fixture
def game_factory() -> type[GameFactory]:
    """Return GameFactory class."""
    return GameFactory


@pytest.fixture
def piece_factory() -> type[GamePieceFactory]:
    """Return GamePieceFactory class."""
    return GamePieceFactory


@pytest.fixture
def move_factory() -> type[GameMoveFactory]:
    """Return GameMoveFactory class."""
    return GameMoveFactory


@pytest.fixture
def chat_factory() -> type[ChatMessageFactory]:
    """Return ChatMessageFactory class."""
    return ChatMessageFactory


@pytest.fixture
def persuasion_factory() -> type[PersuasionAttemptFactory]:
    """Return PersuasionAttemptFactory class."""
    return PersuasionAttemptFactory


@pytest.fixture
def morale_event_factory() -> type[MoraleEventFactory]:
    """Return MoraleEventFactory class."""
    return MoraleEventFactory


# ============================================================================
# Data Fixtures
# ============================================================================

@pytest.fixture
def standard_fen() -> str:
    """Return standard starting position FEN."""
    return STANDARD_FEN


@pytest.fixture
def sample_piece_ids() -> dict:
    """Return sample piece IDs for testing."""
    return SAMPLE_PIECE_IDS


@pytest.fixture
def morale_changes() -> dict:
    """Return morale change values."""
    return MORALE_CHANGES


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_redis() -> Generator[MagicMock, None, None]:
    """
    Mock Redis client for rate limiting tests.

    Yields:
        MagicMock configured as Redis client
    """
    redis_mock = MagicMock()
    redis_mock.get.return_value = None
    redis_mock.setex.return_value = True
    redis_mock.incr.return_value = 1
    redis_mock.ttl.return_value = 60
    redis_mock.delete.return_value = 1
    yield redis_mock


@pytest.fixture
def mock_supabase_client() -> Generator[MagicMock, None, None]:
    """
    Mock Supabase client for database tests.

    Yields:
        MagicMock configured as Supabase client
    """
    client_mock = MagicMock()
    table_mock = MagicMock()
    client_mock.table.return_value = table_mock
    table_mock.select.return_value = table_mock
    table_mock.insert.return_value = table_mock
    table_mock.update.return_value = table_mock
    table_mock.delete.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.neq.return_value = table_mock
    table_mock.gt.return_value = table_mock
    table_mock.gte.return_value = table_mock
    table_mock.lt.return_value = table_mock
    table_mock.lte.return_value = table_mock
    table_mock.order.return_value = table_mock
    table_mock.limit.return_value = table_mock
    table_mock.execute.return_value = MagicMock(data=[], error=None)
    yield client_mock


@pytest.fixture
def valid_jwt_token() -> str:
    """Return a valid JWT token format for testing."""
    # This is a mock token - in real tests you'd generate actual JWTs
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"


@pytest.fixture
def expired_jwt_token() -> str:
    """Return an expired JWT token format for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImV4cCI6MTUxNjE5MDIyMn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"


@pytest.fixture
def invalid_jwt_token() -> str:
    """Return an invalid JWT token format for testing."""
    return "invalid.token.here"


# ============================================================================
# AI Service Mock Variants
# ============================================================================

@pytest.fixture
def mock_gemini_service_refusing(monkeypatch) -> dict:
    """
    Mock Gemini AI service where pieces always refuse moves.

    Returns:
        Mock response data
    """
    from app.services import gemini_service

    async def mock_get_piece_response(*args, **kwargs):
        return PieceResponseOutput(
            will_move=False,
            response_text="I refuse to move! It's too dangerous.",
            morale_change=-5,
        )

    monkeypatch.setattr(
        gemini_service.GeminiService, "get_piece_response", mock_get_piece_response
    )

    return {"piece_response": mock_get_piece_response}


@pytest.fixture
def mock_gemini_service_accepting(monkeypatch) -> dict:
    """
    Mock Gemini AI service where pieces always accept moves.

    Returns:
        Mock response data
    """
    from app.services import gemini_service

    async def mock_get_piece_response(*args, **kwargs):
        return PieceResponseOutput(
            will_move=True,
            response_text="I shall follow your command!",
            morale_change=0,
        )

    monkeypatch.setattr(
        gemini_service.GeminiService, "get_piece_response", mock_get_piece_response
    )

    return {"piece_response": mock_get_piece_response}


@pytest.fixture
def mock_gemini_service_error(monkeypatch) -> dict:
    """
    Mock Gemini AI service that raises errors.

    Returns:
        Mock response data
    """
    from app.services import gemini_service

    async def mock_get_piece_response(*args, **kwargs):
        raise Exception("AI service unavailable")

    async def mock_get_move_analysis(*args, **kwargs):
        raise Exception("AI service unavailable")

    monkeypatch.setattr(
        gemini_service.GeminiService, "get_piece_response", mock_get_piece_response
    )
    monkeypatch.setattr(
        gemini_service.GeminiService, "get_move_analysis", mock_get_move_analysis
    )

    return {
        "piece_response": mock_get_piece_response,
        "analysis": mock_get_move_analysis,
    }
