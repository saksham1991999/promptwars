"""Factory Boy factories for test data generation."""

from __future__ import annotations

import factory
from datetime import datetime, timezone
from uuid import uuid4

from tests.fixtures.data import (
    STANDARD_FEN,
    VALID_TEMPLATES,
    VALID_GAME_MODES,
    VALID_GAME_STATUSES,
    VALID_GAME_RESULTS,
    PERSONALITY_ARCHETYPES,
    MESSAGE_TYPES,
    MORALE_EVENT_TYPES,
    MORALE_CHANGES,
)


class ProfileFactory(factory.Factory):
    """Factory for user profile data."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid4()))
    username = factory.Sequence(lambda n: f"test_user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    avatar_url = None
    games_played = 0
    games_won = 0
    games_lost = 0
    games_drawn = 0
    settings = factory.Dict(
        {
            "theme": "dark",
            "sound": True,
            "voice": False,
            "contrast": False,
            "motion": True,
        }
    )
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class GameFactory(factory.Factory):
    """Factory for game data."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid4()))
    white_player_id = factory.LazyFunction(lambda: str(uuid4()))
    black_player_id = factory.LazyAttribute(lambda obj: "ai" if obj.game_mode == "pvai" else str(uuid4()))
    status = factory.Iterator(VALID_GAME_STATUSES)
    game_mode = factory.Iterator(VALID_GAME_MODES)
    template = factory.Iterator(VALID_TEMPLATES)
    share_code = factory.Sequence(lambda n: f"SHARE{n:03d}")
    fen = STANDARD_FEN
    pgn = ""
    turn = factory.Iterator(["white", "black"])
    result = factory.Iterator([None] + VALID_GAME_RESULTS)
    settings = factory.Dict(
        {
            "surprise_mode": False,
            "turn_timer": None,
            "ai_difficulty": "medium",
        }
    )
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    finished_at = None

    class Params:
        """Factory parameters for specialized game states."""

        active = factory.Trait(
            status="active",
            white_player_id=factory.LazyFunction(lambda: str(uuid4())),
            black_player_id=factory.LazyFunction(lambda: str(uuid4())),
        )

        waiting = factory.Trait(
            status="waiting",
            white_player_id=factory.LazyFunction(lambda: str(uuid4())),
            black_player_id=None,
        )

        completed = factory.Trait(
            status="completed",
            result="white_wins",
            finished_at=factory.LazyFunction(lambda: datetime.now(timezone.utc)),
        )

        pvai = factory.Trait(
            game_mode="pvai",
            black_player_id="ai",
        )

        pvp = factory.Trait(
            game_mode="pvp",
            black_player_id=factory.LazyFunction(lambda: str(uuid4())),
        )


class GamePieceFactory(factory.Factory):
    """Factory for game piece data."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid4()))
    game_id = factory.LazyFunction(lambda: str(uuid4()))
    color = factory.Iterator(["white", "black"])
    piece_type = factory.Iterator(["pawn", "knight", "bishop", "rook", "queen", "king"])
    square = factory.Iterator([f"{file}{rank}" for file in "abcdefgh" for rank in "12345678"])
    morale = 70
    personality = factory.Dict(
        {
            "archetype": "default",
            "traits": ["brave", "loyal"],
            "dialogue_style": "neutral",
            "custom_prompt": "",
            "morale_modifiers": {},
        }
    )
    custom_config = factory.Dict({})
    is_captured = False
    is_promoted = False
    promoted_to = None
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        """Factory parameters for specialized piece states."""

        captured = factory.Trait(
            is_captured=True,
            square=None,
            morale=50,
        )

        promoted = factory.Trait(
            is_promoted=True,
            promoted_to="queen",
            piece_type="queen",
        )

        high_morale = factory.Trait(morale=90)
        low_morale = factory.Trait(morale=30)
        mutinous = factory.Trait(morale=10)

        white = factory.Trait(color="white")
        black = factory.Trait(color="black")

        pawn = factory.Trait(piece_type="pawn")
        knight = factory.Trait(piece_type="knight")
        bishop = factory.Trait(piece_type="bishop")
        rook = factory.Trait(piece_type="rook")
        queen = factory.Trait(piece_type="queen")
        king = factory.Trait(piece_type="king")

    @factory.post_generation
    def set_personality_archetype(obj, create, extracted, **kwargs):
        """Set appropriate archetype based on piece type."""
        piece_type = obj.get("piece_type", "pawn")
        archetypes = PERSONALITY_ARCHETYPES.get(piece_type, ["neutral"])
        obj["personality"]["archetype"] = archetypes[0]


class GameMoveFactory(factory.Factory):
    """Factory for game move data."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid4()))
    game_id = factory.LazyFunction(lambda: str(uuid4()))
    piece_id = factory.LazyFunction(lambda: str(uuid4()))
    player_id = factory.LazyFunction(lambda: str(uuid4()))
    move_number = factory.Sequence(lambda n: n + 1)
    from_square = factory.Iterator(["e2", "d2", "g1", "b1", "c2", "f2"])
    to_square = factory.Iterator(["e4", "d4", "f3", "c3", "c4", "f4"])
    san = factory.Iterator(["e4", "d4", "Nf3", "Nc3", "c4", "f4"])
    fen_after = STANDARD_FEN
    is_capture = False
    is_check = False
    is_checkmate = False
    is_en_passant = False
    is_castle_kingside = False
    is_castle_queenside = False
    is_promotion = False
    promotion_piece = None
    move_quality = factory.Iterator(range(1, 11))
    evaluation = factory.Iterator([0.0, 0.5, -0.5, 1.0, -1.0])
    analysis = factory.Dict(
        {
            "threats": [],
            "opportunities": [],
            "suggested_moves": [],
        }
    )
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        """Factory parameters for specialized move types."""

        capture = factory.Trait(
            is_capture=True,
            san=factory.Iterator(["exd4", "Nxd4", "Bxc6"]),
        )

        check = factory.Trait(
            is_check=True,
            san=factory.Iterator(["Qh5+", "Bb5+", "Nf7+"]),
        )

        checkmate = factory.Trait(
            is_check=True,
            is_checkmate=True,
            san=factory.Iterator(["Qxf7#", "Nf7#", "Rd8#"]),
        )

        en_passant = factory.Trait(
            is_en_passant=True,
            san="exd6e.p.",
        )

        castle_kingside = factory.Trait(
            is_castle_kingside=True,
            san="O-O",
        )

        castle_queenside = factory.Trait(
            is_castle_queenside=True,
            san="O-O-O",
        )

        promotion = factory.Trait(
            is_promotion=True,
            is_capture=factory.Iterator([True, False]),
            san=factory.Iterator(["e8=Q", "exd8=Q", "a8=Q+"]),
            promotion_piece="queen",
        )


class ChatMessageFactory(factory.Factory):
    """Factory for chat message data."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid4()))
    game_id = factory.LazyFunction(lambda: str(uuid4()))
    sender_id = factory.LazyFunction(lambda: str(uuid4()))
    message_type = factory.Iterator(MESSAGE_TYPES)
    sender_name = factory.Iterator(
        [
            "White Player",
            "Black Player",
            "White Knight",
            "Black King",
            "AI Analyst",
            "System",
        ]
    )
    content = factory.Iterator(
        [
            "@Knight move to f3",
            "I shall advance!",
            "I refuse to move into danger!",
            "Solid opening move",
            "Fool! You have fallen into my trap!",
            "Game started",
        ]
    )
    metadata = factory.Dict({})
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        """Factory parameters for specialized message types."""

        player_command = factory.Trait(
            message_type="player_command",
            sender_name="White Player",
            content="@Knight move to f3",
        )

        player_message = factory.Trait(
            message_type="player_message",
            sender_name="White Player",
            content="Good game!",
        )

        piece_response = factory.Trait(
            message_type="piece_response",
            sender_name="White Knight",
            content="For honor and glory!",
        )

        piece_refusal = factory.Trait(
            message_type="piece_refusal",
            sender_name="White Knight",
            content="That square is too dangerous!",
        )

        ai_analysis = factory.Trait(
            message_type="ai_analysis",
            sender_name="AI Analyst",
            content="This move controls the center and develops the piece.",
        )

        king_taunt = factory.Trait(
            message_type="king_taunt",
            sender_name="Black King",
            content="Is that your best move, peasant?",
        )

        system_message = factory.Trait(
            message_type="system",
            sender_name="System",
            content="White wins by checkmate!",
        )

        persuasion_attempt = factory.Trait(
            message_type="persuasion_attempt",
            sender_name="White Player",
            content="Trust me, this move is crucial for our strategy!",
        )

        persuasion_result = factory.Trait(
            message_type="persuasion_result",
            sender_name="System",
            content="Persuasion successful! The piece will move.",
        )


class PersuasionAttemptFactory(factory.Factory):
    """Factory for persuasion attempt data."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid4()))
    game_id = factory.LazyFunction(lambda: str(uuid4()))
    piece_id = factory.LazyFunction(lambda: str(uuid4()))
    player_id = factory.LazyFunction(lambda: str(uuid4()))
    argument_text = factory.Iterator(
        [
            "This move is essential for controlling the center!",
            "Trust me, I see a tactical opportunity.",
            "For the glory of our army, you must advance!",
        ]
    )
    is_voice = False
    success = factory.Iterator([True, False])
    success_probability = factory.Iterator([0.25, 0.5, 0.75, 0.9])
    piece_response = factory.Iterator(
        [
            "Your words have convinced me.",
            "I remain unconvinced. Find another way.",
            "For honor, I shall do as you ask.",
        ]
    )
    evaluation = factory.Dict(
        {
            "logic_score": 25,
            "personality_match": 20,
            "morale_modifier": 10,
            "trust_modifier": 5,
            "urgency_factor": 5,
            "total_probability": 0.65,
        }
    )
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        """Factory parameters for specialized persuasion outcomes."""

        successful = factory.Trait(
            success=True,
            success_probability=factory.Iterator([0.7, 0.8, 0.9]),
            piece_response="Very well, I shall follow your command.",
        )

        failed = factory.Trait(
            success=False,
            success_probability=factory.Iterator([0.1, 0.2, 0.3]),
            piece_response="I cannot in good conscience make that move.",
        )

        voice_argument = factory.Trait(
            is_voice=True,
            argument_text="[Voice recording]",
        )


class MoraleEventFactory(factory.Factory):
    """Factory for morale event data."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid4()))
    game_id = factory.LazyFunction(lambda: str(uuid4()))
    piece_id = factory.LazyFunction(lambda: str(uuid4()))
    event_type = factory.Iterator(MORALE_EVENT_TYPES)
    morale_change = factory.LazyAttribute(lambda obj: MORALE_CHANGES.get(obj["event_type"], 0))
    morale_after = factory.Iterator(range(10, 101, 10))
    description = factory.Iterator(
        [
            "Captured enemy pawn",
            "Lost a comrade",
            "Under attack",
            "Protected by ally",
            "Made a blunder",
            "Waiting without action",
            "Received encouragement",
            "Promoted to Queen!",
            "In strong position",
            "Executed clever tactic",
            "Game started",
            "Persuaded by player",
            "Refused persuasion",
            "Player made false claim",
        ]
    )
    related_piece_id = None
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        """Factory parameters for specialized morale events."""

        positive = factory.Trait(
            event_type=factory.Iterator(["capture_enemy", "promotion", "compliment", "clever_tactic"]),
        )

        negative = factory.Trait(
            event_type=factory.Iterator(["friendly_captured", "blunder", "endangered", "player_lied"]),
        )
