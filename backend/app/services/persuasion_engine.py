"""Persuasion engine — evaluates player arguments and calculates success probability."""

from __future__ import annotations

import logging
import random
from typing import Any

logger = logging.getLogger(__name__)

# Base success rates by morale range
BASE_RATES = {
    (80, 100): 0.90,
    (60, 79): 0.70,
    (40, 59): 0.45,
    (20, 39): 0.25,
    (0, 19): 0.10,
}

# Personality keywords that resonate with each piece type
PERSONALITY_KEYWORDS: dict[str, list[str]] = {
    "pawn": ["team", "sacrifice", "together", "duty", "greater good", "promotion", "advance"],
    "knight": ["glory", "brave", "heroic", "adventure", "charge", "honor", "flashy"],
    "bishop": ["logic", "tactical", "strategy", "position", "calculated", "smart", "reason"],
    "rook": ["duty", "order", "discipline", "defend", "hold", "strong", "fortress"],
    "queen": ["power", "protect", "important", "safe", "retreat", "value", "worth"],
    "king": ["survive", "protect", "castle", "safety", "kingdom", "careful"],
}


class PersuasionEngine:
    """Evaluate persuasion arguments and calculate success probability."""

    @staticmethod
    def get_base_rate(morale: int) -> float:
        """Get the base success rate for a given morale level."""
        for (low, high), rate in BASE_RATES.items():
            if low <= morale <= high:
                return rate
        return 0.45

    @staticmethod
    def calculate_logic_score(
        argument: str,
        is_claim_accurate: bool,
        is_risky: bool,
    ) -> int:
        """Score the logical validity of the player's argument (0-25).

        Checks if the player's factual claims match the board state.
        """
        score = 0

        # Base score for making any argument
        score += 5

        # Accuracy bonus
        if is_claim_accurate:
            score += 10
        else:
            score -= 5  # Penalty for inaccurate claims

        # Argument length/detail bonus (longer = more effort)
        word_count = len(argument.split())
        if word_count >= 10:
            score += 5
        elif word_count >= 5:
            score += 3

        # Risk acknowledgment
        if is_risky and any(word in argument.lower() for word in ["risky", "dangerous", "sacrifice", "trade"]):
            score += 5  # Honesty bonus

        return max(0, min(25, score))

    @staticmethod
    def calculate_personality_match(
        argument: str,
        piece_type: str,
    ) -> int:
        """Score how well the argument matches the piece's personality (0-15)."""
        keywords = PERSONALITY_KEYWORDS.get(piece_type, [])
        argument_lower = argument.lower()

        matches = sum(1 for kw in keywords if kw in argument_lower)

        if matches >= 3:
            return 15
        elif matches >= 2:
            return 10
        elif matches >= 1:
            return 7
        return 2  # Minimum score for trying

    @staticmethod
    def calculate_morale_modifier(morale: int) -> int:
        """Calculate the morale modifier for persuasion (-20 to +20)."""
        if morale >= 80:
            return 20
        elif morale >= 60:
            return 10
        elif morale >= 40:
            return 0
        elif morale >= 20:
            return -10
        return -20

    @staticmethod
    def calculate_trust_modifier(trust_history: float) -> int:
        """Calculate trust modifier based on past promise keeping (-15 to +10)."""
        # trust_history: 0.0 = always lied, 1.0 = always kept promises
        if trust_history >= 0.8:
            return 10
        elif trust_history >= 0.6:
            return 5
        elif trust_history >= 0.4:
            return 0
        elif trust_history >= 0.2:
            return -8
        return -15

    @staticmethod
    def calculate_urgency_factor(
        is_check: bool,
        material_balance: int,
        move_count: int,
    ) -> int:
        """Calculate urgency factor (0-10)."""
        urgency = 0

        if is_check:
            urgency += 5

        # Losing material increases urgency
        if material_balance < -3:
            urgency += 3
        elif material_balance < 0:
            urgency += 1

        # Late game increases urgency
        if move_count > 40:
            urgency += 2

        return min(10, urgency)

    @staticmethod
    def evaluate_persuasion(
        argument: str,
        piece_type: str,
        morale: int,
        is_claim_accurate: bool,
        is_risky: bool,
        trust_history: float = 0.5,
        is_check: bool = False,
        material_balance: int = 0,
        move_count: int = 0,
    ) -> dict[str, Any]:
        """Full persuasion evaluation.

        Returns success probability and breakdown of all factors.
        """
        engine = PersuasionEngine

        base_rate = engine.get_base_rate(morale)
        logic_score = engine.calculate_logic_score(argument, is_claim_accurate, is_risky)
        personality_match = engine.calculate_personality_match(argument, piece_type)
        morale_modifier = engine.calculate_morale_modifier(morale)
        trust_modifier = engine.calculate_trust_modifier(trust_history)
        urgency_factor = engine.calculate_urgency_factor(is_check, material_balance, move_count)

        # Calculate total probability
        # Base rate + weighted contributions from each factor
        total_bonus = (
            (logic_score / 25) * 0.25
            + (personality_match / 15) * 0.15
            + (morale_modifier / 40 + 0.5) * 0.20  # Normalize -20..+20 to 0..1
            + (trust_modifier / 25 + 0.6) * 0.15     # Normalize -15..+10 to 0..1
            + (urgency_factor / 10) * 0.10
        )

        probability = min(0.95, max(0.05, base_rate * 0.5 + total_bonus))

        # Roll the dice
        success = random.random() < probability

        return {
            "success": success,
            "probability": round(probability, 3),
            "logic_score": logic_score,
            "personality_match": personality_match,
            "morale_modifier": morale_modifier,
            "trust_modifier": trust_modifier,
            "urgency_factor": urgency_factor,
        }
