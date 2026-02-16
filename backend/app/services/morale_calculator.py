"""Morale calculator service — event-based morale changes for chess pieces."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Base morale change values per event type
MORALE_EVENTS: dict[str, int] = {
    "capture_enemy": 15,
    "friendly_captured": -10,
    "endangered": -8,
    "protected": 10,
    "blunder": -5,
    "idle": -5,
    "compliment": 5,
    "promotion": 30,
    "good_position": 5,
    "clever_tactic": 10,
    "game_start": 0,
    "persuasion_success": 5,
    "persuasion_fail": -3,
    "player_lied": -15,
}

# Morale thresholds and their behavior descriptions
MORALE_THRESHOLDS = {
    "enthusiastic": (80, 100),
    "normal": (60, 79),
    "reluctant": (40, 59),
    "demoralized": (20, 39),
    "mutinous": (0, 19),
}


class MoraleCalculator:
    """Calculate morale changes and determine piece obedience based on morale levels."""

    @staticmethod
    def calculate_morale_change(
        event_type: str,
        current_morale: int,
        personality: dict[str, Any] | None = None,
    ) -> int:
        """Calculate the morale change for a given event.

        Takes into account the piece's personality modifiers if present.
        """
        base_change = MORALE_EVENTS.get(event_type, 0)

        # Apply personality modifiers
        if personality and "morale_modifiers" in personality:
            modifiers = personality["morale_modifiers"]
            if event_type in modifiers:
                base_change = modifiers[event_type]

        return base_change

    @staticmethod
    def apply_morale_change(current_morale: int, change: int) -> int:
        """Apply a morale change and clamp to 0-100 range."""
        return max(0, min(100, current_morale + change))

    @staticmethod
    def get_morale_category(morale: int) -> str:
        """Get the category name for a morale value."""
        for category, (low, high) in MORALE_THRESHOLDS.items():
            if low <= morale <= high:
                return category
        return "normal"

    @staticmethod
    def get_obedience_rate(morale: int) -> float:
        """Get the base obedience probability for a given morale level.

        Higher morale means higher chance of obeying standard moves.
        """
        if morale >= 80:
            return 0.95
        elif morale >= 60:
            return 0.80
        elif morale >= 40:
            return 0.55
        elif morale >= 20:
            return 0.30
        else:
            return 0.10

    @staticmethod
    def will_piece_obey(
        morale: int,
        is_risky: bool,
        piece_type: str = "pawn",
    ) -> bool:
        """Determine if a piece will obey a move command.

        Based on morale level, risk of the move, and piece personality.
        Pieces with very high morale (90+) almost always obey.
        """
        import random

        base_rate = MoraleCalculator.get_obedience_rate(morale)

        # Risk adjustment
        if is_risky:
            base_rate *= 0.7  # 30% less likely to obey risky moves

        # Piece personality adjustments
        personality_modifiers = {
            "rook": 0.10,     # Loyal soldiers, more obedient
            "knight": -0.05,  # Cocky, might refuse more
            "bishop": 0.0,    # Neutral
            "pawn": 0.05,     # Eager to please
            "queen": -0.10,   # Diva, less obedient for risky
            "king": 0.15,     # Tries to cooperate
        }
        base_rate += personality_modifiers.get(piece_type, 0)

        # Very high morale override
        if morale >= 90 and not is_risky:
            return True

        return random.random() < base_rate

    @staticmethod
    def generate_morale_description(
        event_type: str,
        piece_type: str,
        change: int,
        morale_after: int,
    ) -> str:
        """Generate a human-readable description of a morale change."""
        direction = "increased" if change > 0 else "decreased"
        category = MoraleCalculator.get_morale_category(morale_after)

        descriptions = {
            "capture_enemy": f"{piece_type.capitalize()} feels empowered after the capture! (+{abs(change)})",
            "friendly_captured": f"{piece_type.capitalize()} mourns a fallen ally ({change})",
            "endangered": f"{piece_type.capitalize()} feels threatened and unsafe ({change})",
            "protected": f"{piece_type.capitalize()} feels safe and supported (+{abs(change)})",
            "blunder": f"The bad move shakes everyone's confidence ({change})",
            "idle": f"{piece_type.capitalize()} is restless from sitting idle ({change})",
            "compliment": f"{piece_type.capitalize()} appreciates the kind words (+{abs(change)})",
            "promotion": f"{piece_type.capitalize()} is thrilled about the promotion!! (+{abs(change)})",
            "good_position": f"{piece_type.capitalize()} likes this strategic position (+{abs(change)})",
            "clever_tactic": f"{piece_type.capitalize()} is impressed by the clever play (+{abs(change)})",
            "persuasion_success": f"{piece_type.capitalize()} feels heard and valued (+{abs(change)})",
            "persuasion_fail": f"{piece_type.capitalize()} is frustrated by the failed argument ({change})",
            "player_lied": f"{piece_type.capitalize()} feels betrayed — you broke your promise! ({change})",
        }

        return descriptions.get(
            event_type,
            f"{piece_type.capitalize()} morale {direction} by {abs(change)} (now {morale_after})"
        )

    @staticmethod
    def process_move_morale_effects(
        game_pieces: list[dict[str, Any]],
        moving_piece_id: str,
        is_capture: bool,
        captured_piece_type: str | None,
        is_risky: bool,
        move_quality: int,
    ) -> list[dict[str, Any]]:
        """Process all morale effects from a move.

        Returns a list of morale change events.
        """
        events = []
        calc = MoraleCalculator

        for piece in game_pieces:
            if piece.get("is_captured"):
                continue

            piece_id = piece["id"]
            current_morale = piece.get("morale", 70)
            piece_type = piece.get("piece_type", "pawn")
            personality = piece.get("personality", {})

            if piece_id == moving_piece_id:
                # The piece that moved
                if is_capture:
                    change = calc.calculate_morale_change("capture_enemy", current_morale, personality)
                    new_morale = calc.apply_morale_change(current_morale, change)
                    events.append({
                        "piece_id": piece_id,
                        "event_type": "capture_enemy",
                        "morale_change": change,
                        "morale_after": new_morale,
                        "description": calc.generate_morale_description(
                            "capture_enemy", piece_type, change, new_morale
                        ),
                    })
            elif move_quality <= 3:
                # Bad move affects all friendly pieces
                same_color = piece.get("color") == next(
                    (p.get("color") for p in game_pieces if p["id"] == moving_piece_id),
                    None,
                )
                if same_color:
                    change = calc.calculate_morale_change("blunder", current_morale, personality)
                    new_morale = calc.apply_morale_change(current_morale, change)
                    events.append({
                        "piece_id": piece_id,
                        "event_type": "blunder",
                        "morale_change": change,
                        "morale_after": new_morale,
                        "description": calc.generate_morale_description(
                            "blunder", piece_type, change, new_morale
                        ),
                    })

        return events
