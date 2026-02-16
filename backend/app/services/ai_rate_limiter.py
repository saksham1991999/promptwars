"""AI service rate limiter to enforce cost controls and prevent abuse."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AIRateLimiter:
    """
    Enforce rate limits on AI API calls.

    Tracks per-move, per-game, and daily limits to prevent runaway costs.
    """

    def __init__(
        self,
        max_calls_per_move: int = 5,
        max_calls_per_game: int = 200,
        daily_game_limit: int = 50,
    ):
        """
        Initialize rate limiter with configured limits.

        Args:
            max_calls_per_move: Maximum AI calls per individual move (default: 5)
            max_calls_per_game: Maximum AI calls per game session (default: 200)
            daily_game_limit: Maximum games with AI usage per day (default: 50)
        """
        self.max_calls_per_move = max_calls_per_move
        self.max_calls_per_game = max_calls_per_game
        self.daily_game_limit = daily_game_limit

        # Track AI calls: game_id -> {move_number -> call_count}
        self._move_calls: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))

        # Track total calls per game: game_id -> total_count
        self._game_calls: dict[str, int] = defaultdict(int)

        # Track daily game usage: date -> set of game_ids
        self._daily_games: dict[str, set[str]] = defaultdict(set)

    def check_and_increment(
        self, game_id: str, move_number: int, endpoint: str = "default"
    ) -> tuple[bool, str | None]:
        """
        Check if AI call is allowed and increment counters.

        Args:
            game_id: Game identifier
            move_number: Current move number
            endpoint: AI endpoint being called (for logging)

        Returns:
            Tuple of (is_allowed, error_message)
            - is_allowed: True if call is within limits
            - error_message: None if allowed, error description if blocked
        """
        # Check daily game limit
        today = datetime.now().date().isoformat()
        if len(self._daily_games[today]) >= self.daily_game_limit:
            if game_id not in self._daily_games[today]:
                error_msg = (
                    f"Daily AI game limit reached ({self.daily_game_limit} games). "
                    "Falling back to template responses."
                )
                logger.warning("AI rate limit: %s", error_msg)
                return False, error_msg

        # Check per-move limit
        move_calls = self._move_calls[game_id][move_number]
        if move_calls >= self.max_calls_per_move:
            error_msg = (
                f"Per-move AI limit reached ({self.max_calls_per_move} calls for move {move_number}). "
                "Using fallback response."
            )
            logger.warning("AI rate limit: %s", error_msg)
            return False, error_msg

        # Check per-game limit
        game_calls = self._game_calls[game_id]
        if game_calls >= self.max_calls_per_game:
            error_msg = (
                f"Per-game AI limit reached ({self.max_calls_per_game} calls). "
                "Using fallback responses for remainder of game."
            )
            logger.warning("AI rate limit: %s", error_msg)
            return False, error_msg

        # All checks passed - increment counters
        self._move_calls[game_id][move_number] += 1
        self._game_calls[game_id] += 1
        self._daily_games[today].add(game_id)

        logger.debug(
            "AI call allowed - game=%s, move=%s, endpoint=%s, "
            "move_calls=%s/%s, game_calls=%s/%s",
            game_id[:8],
            move_number,
            endpoint,
            move_calls + 1,
            self.max_calls_per_move,
            game_calls + 1,
            self.max_calls_per_game,
        )

        return True, None

    def get_stats(self, game_id: str | None = None) -> dict:
        """
        Get rate limit statistics.

        Args:
            game_id: Optional game ID for game-specific stats

        Returns:
            Dict with usage statistics
        """
        today = datetime.now().date().isoformat()

        if game_id:
            # Game-specific stats
            return {
                "game_id": game_id,
                "total_calls": self._game_calls.get(game_id, 0),
                "max_calls_per_game": self.max_calls_per_game,
                "remaining_calls": max(
                    0, self.max_calls_per_game - self._game_calls.get(game_id, 0)
                ),
                "move_calls": dict(self._move_calls.get(game_id, {})),
            }

        # Global stats
        return {
            "daily_games_today": len(self._daily_games[today]),
            "daily_game_limit": self.daily_game_limit,
            "remaining_daily_games": max(
                0, self.daily_game_limit - len(self._daily_games[today])
            ),
            "total_active_games": len(self._game_calls),
            "limits": {
                "max_calls_per_move": self.max_calls_per_move,
                "max_calls_per_game": self.max_calls_per_game,
                "daily_game_limit": self.daily_game_limit,
            },
        }

    def reset_game(self, game_id: str):
        """
        Reset rate limit counters for a specific game.

        Useful for testing or if a game is restarted.

        Args:
            game_id: Game identifier
        """
        self._move_calls.pop(game_id, None)
        self._game_calls.pop(game_id, None)
        logger.info("Reset AI rate limits for game %s", game_id[:8])

    def cleanup_old_data(self, days_to_keep: int = 7):
        """
        Remove old daily game data to prevent memory leaks.

        Args:
            days_to_keep: Number of days of data to retain (default: 7)
        """
        cutoff_date = (datetime.now().date() - timedelta(days=days_to_keep)).isoformat()

        dates_to_remove = [
            date for date in self._daily_games.keys() if date < cutoff_date
        ]

        for date in dates_to_remove:
            del self._daily_games[date]

        if dates_to_remove:
            logger.info(
                "Cleaned up AI rate limiter data: removed %s days", len(dates_to_remove)
            )


# Global instance
ai_rate_limiter = AIRateLimiter()
