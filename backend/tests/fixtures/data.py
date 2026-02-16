"""Static test data for Chess Alive tests."""

from __future__ import annotations

from datetime import datetime, timezone

# Standard chess positions
STANDARD_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# After 1. e4
E4_OPENING_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"

# After 1. e4 e5
ITALIAN_GAME_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"

# Middlegame position (complex)
MIDDLEGAME_FEN = "r1bq1rk1/ppp2ppp/2np1n2/1B2p3/1b2P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 1"

# Endgame position (king and pawn)
ENDGAME_FEN = "8/5k2/8/4P3/8/8/5K2/8 w - - 0 1"

# Checkmate position (Scholar's mate)
SCHOLARS_MATE_FEN = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1"

# Checkmate position (white to move is checkmated)
CHECKMATE_FEN = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1"

# Stalemate position
STALEMATE_FEN = "k7/8/8/8/8/8/8/4K2R w - - 0 1"

# Threefold repetition test position
THREEFOLD_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Insufficient material (king vs king)
INSUFFICIENT_MATERIAL_FEN = "4k3/8/8/8/8/8/8/4K3 w - - 0 1"

# Fifty-move rule position
FIFTY_MOVE_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 50 1"

# En passant position
EN_PASSANT_FEN = "rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 1"

# Castling rights (all rights available)
FULL_CASTLING_FEN = "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"

# No castling rights
NO_CASTLING_FEN = "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w - - 0 1"

# Pinned piece position
PINNED_PIECE_FEN = "4k3/4r3/8/8/8/3B4/8/4K3 w - - 0 1"

# Discovered check position
DISCOVERED_CHECK_FEN = "4k3/8/8/8/3b4/8/4P3/4K3 w - - 0 1"

# Double check position
DOUBLE_CHECK_FEN = "4k3/6N1/8/8/8/8/8/4K2R w K - 0 1"

# Sample move sequences
SCHOLARS_MATE_MOVES = [
    {"from": "e2", "to": "e4", "san": "e4"},
    {"from": "e7", "to": "e5", "san": "e5"},
    {"from": "d1", "to": "h5", "san": "Qh5"},
    {"from": "b8", "to": "c6", "san": "Nc6"},
    {"from": "f1", "to": "c4", "san": "Bc4"},
    {"from": "g8", "to": "f6", "san": "Nf6"},
    {"from": "h5", "to": "f7", "san": "Qxf7#"},
]

# Standard piece setup for testing
STANDARD_PIECE_SETUP = [
    # White pieces (back rank)
    {"color": "white", "piece_type": "rook", "square": "a1", "morale": 70},
    {"color": "white", "piece_type": "knight", "square": "b1", "morale": 70},
    {"color": "white", "piece_type": "bishop", "square": "c1", "morale": 70},
    {"color": "white", "piece_type": "queen", "square": "d1", "morale": 70},
    {"color": "white", "piece_type": "king", "square": "e1", "morale": 70},
    {"color": "white", "piece_type": "bishop", "square": "f1", "morale": 70},
    {"color": "white", "piece_type": "knight", "square": "g1", "morale": 70},
    {"color": "white", "piece_type": "rook", "square": "h1", "morale": 70},
    # White pawns
    {"color": "white", "piece_type": "pawn", "square": "a2", "morale": 70},
    {"color": "white", "piece_type": "pawn", "square": "b2", "morale": 70},
    {"color": "white", "piece_type": "pawn", "square": "c2", "morale": 70},
    {"color": "white", "piece_type": "pawn", "square": "d2", "morale": 70},
    {"color": "white", "piece_type": "pawn", "square": "e2", "morale": 70},
    {"color": "white", "piece_type": "pawn", "square": "f2", "morale": 70},
    {"color": "white", "piece_type": "pawn", "square": "g2", "morale": 70},
    {"color": "white", "piece_type": "pawn", "square": "h2", "morale": 70},
    # Black pawns
    {"color": "black", "piece_type": "pawn", "square": "a7", "morale": 70},
    {"color": "black", "piece_type": "pawn", "square": "b7", "morale": 70},
    {"color": "black", "piece_type": "pawn", "square": "c7", "morale": 70},
    {"color": "black", "piece_type": "pawn", "square": "d7", "morale": 70},
    {"color": "black", "piece_type": "pawn", "square": "e7", "morale": 70},
    {"color": "black", "piece_type": "pawn", "square": "f7", "morale": 70},
    {"color": "black", "piece_type": "pawn", "square": "g7", "morale": 70},
    {"color": "black", "piece_type": "pawn", "square": "h7", "morale": 70},
    # Black pieces (back rank)
    {"color": "black", "piece_type": "rook", "square": "a8", "morale": 70},
    {"color": "black", "piece_type": "knight", "square": "b8", "morale": 70},
    {"color": "black", "piece_type": "bishop", "square": "c8", "morale": 70},
    {"color": "black", "piece_type": "queen", "square": "d8", "morale": 70},
    {"color": "black", "piece_type": "king", "square": "e8", "morale": 70},
    {"color": "black", "piece_type": "bishop", "square": "f8", "morale": 70},
    {"color": "black", "piece_type": "knight", "square": "g8", "morale": 70},
    {"color": "black", "piece_type": "rook", "square": "h8", "morale": 70},
]

# Personality archetypes by piece type
PERSONALITY_ARCHETYPES = {
    "pawn": ["loyal_soldier", "reluctant_fighter", "ambitious_grunt"],
    "knight": ["daring_hero", "lone_wolf", "chivalrous_guardian"],
    "bishop": ["wise_counselor", "devoted_mystic", "calculating_strategist"],
    "rook": ["steadfast_defender", "siege_master", "unyielding_fortress"],
    "queen": ["ruthless_conqueror", "noble_protector", "ambitious_ruler"],
    "king": ["cautious_monarch", "inspiring_leader", "paranoid_ruler"],
    "chancellor": ["tactical_genius", "field_commander"],
    "archbishop": ["holy_warrior", "divine_tactician"],
    "amazon": ["fearless_warrior", "legendary_champion"],
    "camel": ["desert_wanderer", "enduring_traveler"],
    "nightrider": ["shadow_striker", "midnight_raider"],
    "grasshopper": ["unconventional_tactician", "surprise_attacker"],
    "cannon": ["artillery_expert", "long_range_specialist"],
    "berolina_pawn": ["cunning_infiltrator", "unpredictable_fighter"],
}

# Message types for chat
MESSAGE_TYPES = [
    "player_command",
    "player_message",
    "piece_response",
    "piece_refusal",
    "ai_analysis",
    "ai_suggestion",
    "king_taunt",
    "king_reaction",
    "system",
    "persuasion_attempt",
    "persuasion_result",
]

# Morale event types
MORALE_EVENT_TYPES = [
    "capture_enemy",
    "friendly_captured",
    "endangered",
    "protected",
    "blunder",
    "idle",
    "compliment",
    "promotion",
    "good_position",
    "clever_tactic",
    "game_start",
    "persuasion_success",
    "persuasion_fail",
    "player_lied",
]

# Morale change values
MORALE_CHANGES = {
    "capture_enemy": 15,
    "friendly_captured": -20,
    "endangered": -10,
    "protected": 5,
    "blunder": -15,
    "idle": -5,
    "compliment": 10,
    "promotion": 25,
    "good_position": 5,
    "clever_tactic": 10,
    "game_start": 0,
    "persuasion_success": 5,
    "persuasion_fail": -5,
    "player_lied": -20,
}

# Sample datetime for testing
SAMPLE_DATETIME = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
SAMPLE_DATETIME_ISO = "2024-01-15T12:00:00+00:00"

# Valid templates
VALID_TEMPLATES = ["classic", "power_chess", "leaper_madness", "hopper_havoc", "pawn_revolution"]

# Valid game modes
VALID_GAME_MODES = ["pvp", "pvai"]

# Valid game statuses
VALID_GAME_STATUSES = ["waiting", "setup", "active", "completed", "abandoned"]

# Valid game results
VALID_GAME_RESULTS = ["white_wins", "black_wins", "draw", "stalemate", "abandoned"]

# Standard sample share codes
SAMPLE_SHARE_CODES = ["ABC123", "XYZ789", "DEF456", "GHI012", "JKL345"]

# Sample piece IDs for testing
SAMPLE_PIECE_IDS = {
    "white": {
        "king": "white-king-e1",
        "queen": "white-queen-d1",
        "rook_a": "white-rook-a1",
        "rook_h": "white-rook-h1",
        "bishop_c": "white-bishop-c1",
        "bishop_f": "white-bishop-f1",
        "knight_b": "white-knight-b1",
        "knight_g": "white-knight-g1",
    },
    "black": {
        "king": "black-king-e8",
        "queen": "black-queen-d8",
        "rook_a": "black-rook-a8",
        "rook_h": "black-rook-h8",
        "bishop_c": "black-bishop-c8",
        "bishop_f": "black-bishop-f8",
        "knight_b": "black-knight-b8",
        "knight_g": "black-knight-g8",
    },
}
