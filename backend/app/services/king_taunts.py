"""King taunt generator — contextual taunts from the opponent's King."""

from __future__ import annotations

import random
from typing import Any


# Template taunts by game state category
TAUNTS: dict[str, list[str]] = {
    "piece_captured": [
        "Lost your {piece}? How careless.",
        "Down material already? Tsk tsk.",
        "Your {piece} won't be missed... by me.",
        "One less piece for you to worry about!",
        "That {piece} had so much potential. Had.",
    ],
    "blunder": [
        "Did you just hang your {piece}? Wow.",
        "Even my Pawns saw that coming.",
        "Are you trying to lose? Impressive blunder.",
        "I almost feel bad. Almost.",
        "That was... a choice. A terrible one.",
    ],
    "check": [
        "Run, little King, run!",
        "Nowhere to hide!",
        "Check! How does that feel?",
        "Your King is sweating, I can tell.",
        "Better find cover, your Majesty!",
    ],
    "winning": [
        "This is almost too easy.",
        "Should we just call it?",
        "I can do this all day.",
        "Your army is crumbling.",
        "Resistance is futile at this point.",
    ],
    "losing": [
        "A lucky move. This isn't over.",
        "I've come back from worse.",
        "Don't celebrate yet.",
        "Enjoy it while it lasts.",
        "One good move doesn't make you a champion.",
    ],
    "stalemate_risk": [
        "Don't you dare stalemate me!",
        "I want a proper victory!",
        "Be careful, or nobody wins.",
    ],
    "great_move": [
        "...I'll admit, that was decent.",
        "Lucky shot. Won't happen again.",
        "Okay, you have SOME skill.",
        "Not bad. For an amateur.",
    ],
    "game_start": [
        "Ready to lose?",
        "Let's see what you've got.",
        "May the best player win. That's me.",
        "I've already planned your defeat.",
    ],
    "opponent_resigned": [
        "Running away? Smart choice.",
        "I accept your surrender.",
    ],
}


class KingTauntGenerator:
    """Generate contextual taunts from the opponent's King."""

    @staticmethod
    def generate_taunt(
        trigger_event: str,
        material_balance: int = 0,
        move_count: int = 0,
        piece_type: str | None = None,
    ) -> str | None:
        """Generate a taunt based on the game event.

        Args:
            trigger_event: Type of event that triggered the taunt.
            material_balance: Positive = taunting King is winning.
            move_count: Current move count.
            piece_type: Type of piece involved (for captured piece taunts).

        Returns:
            Taunt text or None if no taunt is appropriate.
        """
        # Determine the best taunt category
        category = trigger_event

        # If there's no direct match, infer from game state
        if category not in TAUNTS:
            if material_balance > 3:
                category = "winning"
            elif material_balance < -3:
                category = "losing"
            else:
                return None  # No taunt for neutral states

        templates = TAUNTS.get(category, [])
        if not templates:
            return None

        taunt = random.choice(templates)

        # Fill in template variables
        if piece_type:
            taunt = taunt.replace("{piece}", piece_type.capitalize())
        else:
            taunt = taunt.replace("{piece}", "piece")

        return taunt

    @staticmethod
    def should_taunt(trigger_event: str, move_count: int) -> bool:
        """Determine if a taunt should be generated for this event.

        Not every move needs a taunt — they should feel natural, not spammy.
        """
        # Always taunt on these events
        always_taunt = {"check", "blunder", "game_start", "piece_captured"}
        if trigger_event in always_taunt:
            return True

        # Occasional taunts for other events (30% chance)
        return random.random() < 0.3

    @staticmethod
    def get_taunt_intensity(material_balance: int, trigger_event: str) -> int:
        """Rate the intensity of the taunt (1-5)."""
        intensity = 2  # Default

        if trigger_event in ("check", "blunder"):
            intensity = 4
        elif trigger_event == "piece_captured":
            intensity = 3
        elif trigger_event == "great_move":
            intensity = 1  # Grudging respect

        # More intense when winning big
        if material_balance > 5:
            intensity = min(5, intensity + 1)

        return intensity
