"""AI cost tracking service to monitor token usage and estimate costs."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AICostTracker:
    """
    Track AI token usage and calculate costs.

    Uses Gemini Flash pricing: $0.075/1M input tokens, $0.30/1M output tokens.
    """

    # Gemini Flash pricing (as of Jan 2025)
    GEMINI_PRICING = {
        "input_tokens_per_1m": 0.075,  # $0.075 per 1M input tokens
        "output_tokens_per_1m": 0.30,  # $0.30 per 1M output tokens
    }

    def __init__(self):
        """Initialize cost tracker with empty usage data."""
        # Track usage by game: game_id -> {input_tokens, output_tokens, calls, cost}
        self._game_usage: dict[str, dict[str, int | float]] = defaultdict(
            lambda: {"input_tokens": 0, "output_tokens": 0, "calls": 0, "cost_usd": 0.0}
        )

        # Track daily usage: date -> {input_tokens, output_tokens, calls, cost, games}
        self._daily_usage: dict[str, dict] = defaultdict(
            lambda: {
                "input_tokens": 0,
                "output_tokens": 0,
                "calls": 0,
                "cost_usd": 0.0,
                "games": set(),
            }
        )

    def record_usage(
        self,
        game_id: str,
        input_tokens: int,
        output_tokens: int,
        endpoint: str = "default",
    ):
        """
        Record AI token usage and calculate costs.

        Args:
            game_id: Game identifier
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            endpoint: AI endpoint called (for logging)
        """
        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * self.GEMINI_PRICING[
            "input_tokens_per_1m"
        ]
        output_cost = (output_tokens / 1_000_000) * self.GEMINI_PRICING[
            "output_tokens_per_1m"
        ]
        total_cost = input_cost + output_cost

        # Update game usage
        game_usage = self._game_usage[game_id]
        game_usage["input_tokens"] += input_tokens
        game_usage["output_tokens"] += output_tokens
        game_usage["calls"] += 1
        game_usage["cost_usd"] += total_cost

        # Update daily usage
        today = datetime.now().date().isoformat()
        daily = self._daily_usage[today]
        daily["input_tokens"] += input_tokens
        daily["output_tokens"] += output_tokens
        daily["calls"] += 1
        daily["cost_usd"] += total_cost
        daily["games"].add(game_id)

        logger.debug(
            "AI cost tracked - game=%s, endpoint=%s, "
            "input=%s, output=%s, cost=$%.4f",
            game_id[:8],
            endpoint,
            input_tokens,
            output_tokens,
            total_cost,
        )

    def get_game_cost(self, game_id: str) -> dict:
        """
        Get cost statistics for a specific game.

        Args:
            game_id: Game identifier

        Returns:
            Dict with usage and cost data
        """
        usage = self._game_usage.get(game_id)
        if not usage:
            return {
                "game_id": game_id,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "calls": 0,
                "cost_usd": 0.0,
            }

        return {
            "game_id": game_id,
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "total_tokens": usage["input_tokens"] + usage["output_tokens"],
            "calls": usage["calls"],
            "cost_usd": round(usage["cost_usd"], 4),
        }

    def get_daily_cost(self, date: str | None = None) -> dict:
        """
        Get cost statistics for a specific day.

        Args:
            date: Date in ISO format (YYYY-MM-DD), defaults to today

        Returns:
            Dict with daily usage and cost data
        """
        if date is None:
            date = datetime.now().date().isoformat()

        usage = self._daily_usage.get(date)
        if not usage:
            return {
                "date": date,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "calls": 0,
                "games": 0,
                "cost_usd": 0.0,
            }

        return {
            "date": date,
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "total_tokens": usage["input_tokens"] + usage["output_tokens"],
            "calls": usage["calls"],
            "games": len(usage["games"]),
            "cost_usd": round(usage["cost_usd"], 4),
        }

    def get_monthly_estimate(self) -> dict:
        """
        Estimate monthly cost based on last 7 days average.

        Returns:
            Dict with estimated monthly cost and breakdown
        """
        # Get last 7 days of data
        today = datetime.now().date()
        last_7_days = [
            (today - timedelta(days=i)).isoformat() for i in range(7)
        ]

        total_cost = 0.0
        total_calls = 0
        total_games = set()

        for date in last_7_days:
            usage = self._daily_usage.get(date)
            if usage:
                total_cost += usage["cost_usd"]
                total_calls += usage["calls"]
                total_games.update(usage["games"])

        # Calculate averages
        avg_daily_cost = total_cost / 7
        avg_daily_games = len(total_games) / 7

        # Estimate monthly (30 days)
        estimated_monthly_cost = avg_daily_cost * 30

        return {
            "period": "last_7_days",
            "total_cost_usd": round(total_cost, 4),
            "total_calls": total_calls,
            "unique_games": len(total_games),
            "avg_daily_cost_usd": round(avg_daily_cost, 4),
            "avg_daily_games": round(avg_daily_games, 2),
            "estimated_monthly_cost_usd": round(estimated_monthly_cost, 2),
        }

    def get_all_stats(self) -> dict:
        """
        Get comprehensive cost statistics.

        Returns:
            Dict with all available statistics
        """
        today = datetime.now().date().isoformat()

        return {
            "today": self.get_daily_cost(today),
            "monthly_estimate": self.get_monthly_estimate(),
            "pricing": self.GEMINI_PRICING,
            "total_active_games": len(self._game_usage),
        }

    def cleanup_old_data(self, days_to_keep: int = 30):
        """
        Remove old usage data to prevent memory leaks.

        Args:
            days_to_keep: Number of days of data to retain (default: 30)
        """
        cutoff_date = (datetime.now().date() - timedelta(days=days_to_keep)).isoformat()

        dates_to_remove = [
            date for date in self._daily_usage.keys() if date < cutoff_date
        ]

        for date in dates_to_remove:
            del self._daily_usage[date]

        if dates_to_remove:
            logger.info(
                "Cleaned up AI cost tracker data: removed %s days", len(dates_to_remove)
            )


# Global instance
ai_cost_tracker = AICostTracker()
