"""Piece response templates for fallback (when AI is unavailable)."""

from __future__ import annotations

import random

# Acceptance templates by piece type
ACCEPT_TEMPLATES: dict[str, list[str]] = {
    "pawn": [
        "For the king! I march to {sq}!",
        "Yes sir! Moving to {sq} right away!",
        "One step closer to glory... heading to {sq}!",
    ],
    "knight": [
        "*leaps dramatically* To {sq}! Watch this!",
        "CHARGE! {sq}, here I come!",
        "A daring move to {sq}? I love it!",
    ],
    "bishop": [
        "A logical choice. Repositioning to {sq}.",
        "I see the diagonal. Moving to {sq} as planned.",
        "Calculated. {sq} provides excellent coverage.",
    ],
    "rook": [
        "Acknowledged. Moving to {sq}, sir.",
        "Orders received. Deploying to {sq}.",
        "Affirmative. {sq}. Consider it done.",
    ],
    "queen": [
        "About time I got involved. {sq} it is.",
        "*adjusts crown* Fine, {sq}. You're welcome.",
        "Moving to {sq}. This better be worth it.",
    ],
    "king": [
        "I hope you know what you're doing... moving to {sq}.",
        "Is it safe? ...Fine, {sq}.",
        "Moving to {sq}. Please protect me!",
    ],
}

# Refusal templates by piece type
REFUSE_TEMPLATES: dict[str, list[str]] = {
    "pawn": [
        "I-I don't think I should... it looks scary over there!",
        "My morale is too low... I can barely move!",
        "Please don't make me go... not yet!",
    ],
    "knight": [
        "Even I have limits! That's suicide!",
        "No way! I'm bold, not stupid!",
        "I refuse! My glory days aren't ending here!",
    ],
    "bishop": [
        "I've analyzed the position. The answer is no.",
        "Strategically inadvisable. I must decline.",
        "My analysis suggests this is a terrible idea.",
    ],
    "rook": [
        "Negative. That order would compromise the position.",
        "I cannot comply. The risk is unacceptable.",
        "Standing down. That's not a defensible position.",
    ],
    "queen": [
        "Excuse me? I'm not walking into that trap.",
        "I think NOT. My life is worth more than that.",
        "Hard pass. Find someone else to sacrifice.",
    ],
    "king": [
        "ABSOLUTELY NOT! Are you trying to get me killed?!",
        "I'm the King! I refuse that reckless move!",
        "No! My safety is paramount!",
    ],
}


def get_piece_accept_text(piece_type: str, target_square: str) -> str:
    """
    Get random acceptance text for a piece move.

    Args:
        piece_type: Type of chess piece (pawn, knight, bishop, rook, queen, king)
        target_square: Target square in algebraic notation (e.g., "e4")

    Returns:
        Formatted acceptance message
    """
    templates = ACCEPT_TEMPLATES.get(piece_type, ACCEPT_TEMPLATES["pawn"])
    return random.choice(templates).format(sq=target_square)


def get_piece_refuse_text(piece_type: str, morale: int) -> str:
    """
    Get random refusal text for a piece move.

    Args:
        piece_type: Type of chess piece (pawn, knight, bishop, rook, queen, king)
        morale: Current morale level (0-100) - currently unused but reserved

    Returns:
        Refusal message
    """
    templates = REFUSE_TEMPLATES.get(piece_type, REFUSE_TEMPLATES["pawn"])
    return random.choice(templates)
