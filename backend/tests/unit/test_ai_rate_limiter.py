"""Unit tests for the AI rate limiter service."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.services.ai_rate_limiter import AIRateLimiter


class TestInitialization:
    """Tests for AIRateLimiter initialization."""

    @pytest.mark.unit
    def test_default_limits(self):
        """Should initialize with default limits."""
        limiter = AIRateLimiter()
        assert limiter.max_calls_per_move == 5
        assert limiter.max_calls_per_game == 200
        assert limiter.daily_game_limit == 50

    @pytest.mark.unit
    def test_custom_limits(self):
        """Should accept custom limits."""
        limiter = AIRateLimiter(
            max_calls_per_move=10,
            max_calls_per_game=500,
            daily_game_limit=100,
        )
        assert limiter.max_calls_per_move == 10
        assert limiter.max_calls_per_game == 500
        assert limiter.daily_game_limit == 100


class TestCheckAndIncrement:
    """Tests for AIRateLimiter.check_and_increment method."""

    @pytest.fixture
    def limiter(self):
        """Create a fresh rate limiter."""
        return AIRateLimiter()

    @pytest.mark.unit
    def test_first_call_allowed(self, limiter):
        """First call should be allowed."""
        allowed, error = limiter.check_and_increment("game-1", 1)
        assert allowed is True
        assert error is None

    @pytest.mark.unit
    def test_calls_within_move_limit_allowed(self, limiter):
        """Calls within per-move limit should be allowed."""
        for i in range(5):
            allowed, _ = limiter.check_and_increment("game-1", 1)
            assert allowed is True

    @pytest.mark.unit
    def test_per_move_limit_blocked(self, limiter):
        """Calls exceeding per-move limit should be blocked."""
        # Use up the limit
        for _ in range(5):
            limiter.check_and_increment("game-1", 1)

        # Next call should be blocked
        allowed, error = limiter.check_and_increment("game-1", 1)
        assert allowed is False
        assert error is not None
        assert "Per-move AI limit reached" in error

    @pytest.mark.unit
    def test_different_moves_have_separate_limits(self, limiter):
        """Different moves should have separate limits."""
        # Use up limit for move 1
        for _ in range(5):
            limiter.check_and_increment("game-1", 1)

        # Move 2 should still be allowed
        allowed, _ = limiter.check_and_increment("game-1", 2)
        assert allowed is True

    @pytest.mark.unit
    def test_per_game_limit_blocked(self, limiter):
        """Calls exceeding per-game limit should be blocked."""
        # Use up the game limit across multiple moves
        for move_num in range(40):
            for _ in range(5):  # 5 calls per move
                limiter.check_and_increment("game-1", move_num)

        # Next call should be blocked
        allowed, error = limiter.check_and_increment("game-1", 41)
        assert allowed is False
        assert error is not None
        assert "Per-game AI limit reached" in error

    @pytest.mark.unit
    def test_different_games_have_separate_limits(self, limiter):
        """Different games should have separate limits."""
        # Use up limit for game 1
        for move_num in range(40):
            for _ in range(5):
                limiter.check_and_increment("game-1", move_num)

        # Game 2 should still be allowed
        allowed, _ = limiter.check_and_increment("game-2", 1)
        assert allowed is True

    @pytest.mark.unit
    @patch("app.services.ai_rate_limiter.datetime")
    def test_daily_game_limit_blocked(self, mock_datetime, limiter):
        """Calls exceeding daily game limit should be blocked."""
        # Mock today's date
        mock_now = datetime(2024, 1, 15, 12, 0, 0)
        mock_datetime.now.return_value = mock_now

        # Register 50 games for today
        for i in range(50):
            limiter.check_and_increment(f"game-{i}", 1)

        # Next game should be blocked
        allowed, error = limiter.check_and_increment("game-new", 1)
        assert allowed is False
        assert error is not None
        assert "Daily AI game limit reached" in error

    @pytest.mark.unit
    @patch("app.services.ai_rate_limiter.datetime")
    def test_existing_game_not_blocked_by_daily_limit(self, mock_datetime, limiter):
        """Existing games should not be blocked by daily game limit."""
        # Mock today's date
        mock_now = datetime(2024, 1, 15, 12, 0, 0)
        mock_datetime.now.return_value = mock_now

        # Register 50 games for today
        for i in range(50):
            limiter.check_and_increment(f"game-{i}", 1)

        # Existing game should still be allowed
        allowed, _ = limiter.check_and_increment("game-0", 2)
        assert allowed is True


class TestGetStats:
    """Tests for AIRateLimiter.get_stats method."""

    @pytest.fixture
    def limiter_with_usage(self):
        """Create a rate limiter with some usage."""
        limiter = AIRateLimiter()
        # Add some usage
        for _ in range(3):
            limiter.check_and_increment("game-1", 1)
        for _ in range(2):
            limiter.check_and_increment("game-1", 2)
        return limiter

    @pytest.mark.unit
    def test_game_specific_stats(self, limiter_with_usage):
        """Should return stats for specific game."""
        stats = limiter_with_usage.get_stats("game-1")

        assert stats["game_id"] == "game-1"
        assert stats["total_calls"] == 5
        assert stats["max_calls_per_game"] == 200
        assert stats["remaining_calls"] == 195
        assert stats["move_calls"] == {1: 3, 2: 2}

    @pytest.mark.unit
    def test_global_stats(self, limiter_with_usage):
        """Should return global stats when no game specified."""
        stats = limiter_with_usage.get_stats()

        assert "daily_games_today" in stats
        assert "daily_game_limit" in stats
        assert "remaining_daily_games" in stats
        assert "total_active_games" in stats
        assert "limits" in stats
        assert stats["limits"]["max_calls_per_move"] == 5

    @pytest.mark.unit
    def test_stats_for_unknown_game(self):
        """Should return zero stats for unknown game."""
        limiter = AIRateLimiter()
        stats = limiter.get_stats("unknown-game")

        assert stats["game_id"] == "unknown-game"
        assert stats["total_calls"] == 0
        assert stats["remaining_calls"] == 200


class TestResetGame:
    """Tests for AIRateLimiter.reset_game method."""

    @pytest.mark.unit
    def test_reset_clears_game_counters(self):
        """Reset should clear all counters for a game."""
        limiter = AIRateLimiter()

        # Add usage
        for _ in range(5):
            limiter.check_and_increment("game-1", 1)

        # Reset
        limiter.reset_game("game-1")

        # Check stats are cleared
        stats = limiter.get_stats("game-1")
        assert stats["total_calls"] == 0

        # Should be able to make calls again
        allowed, _ = limiter.check_and_increment("game-1", 1)
        assert allowed is True

    @pytest.mark.unit
    def test_reset_does_not_affect_other_games(self):
        """Reset should not affect other games."""
        limiter = AIRateLimiter()

        # Add usage to both games
        limiter.check_and_increment("game-1", 1)
        limiter.check_and_increment("game-2", 1)

        # Reset game-1 only
        limiter.reset_game("game-1")

        # game-2 should still have usage
        stats = limiter.get_stats("game-2")
        assert stats["total_calls"] == 1


class TestCleanupOldData:
    """Tests for AIRateLimiter.cleanup_old_data method."""

    @pytest.mark.unit
    @patch("app.services.ai_rate_limiter.datetime")
    def test_cleanup_removes_old_daily_data(self, mock_datetime):
        """Should remove daily data older than specified days."""
        limiter = AIRateLimiter()

        # Mock current date
        mock_now = datetime(2024, 1, 15, 12, 0, 0)
        mock_datetime.now.return_value = mock_now

        # Add some old daily data
        limiter._daily_games["2024-01-01"] = {"game-1", "game-2"}
        limiter._daily_games["2024-01-10"] = {"game-3"}
        limiter._daily_games["2024-01-14"] = {"game-4"}  # Recent
        limiter._daily_games["2024-01-15"] = {"game-5"}  # Today

        # Cleanup with 7 days retention
        limiter.cleanup_old_data(days_to_keep=7)

        # Old data should be removed
        assert "2024-01-01" not in limiter._daily_games
        assert "2024-01-10" not in limiter._daily_games

        # Recent data should remain
        assert "2024-01-14" in limiter._daily_games
        assert "2024-01-15" in limiter._daily_games


class TestGlobalInstance:
    """Tests for the global ai_rate_limiter instance."""

    @pytest.mark.unit
    def test_global_instance_exists(self):
        """Global ai_rate_limiter instance should exist."""
        from app.services.ai_rate_limiter import ai_rate_limiter

        assert ai_rate_limiter is not None
        assert isinstance(ai_rate_limiter, AIRateLimiter)
