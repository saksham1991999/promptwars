"""Gemini AI service — Pydantic AI agent orchestration with fallback responses.

Uses Pydantic AI agents for piece responses, analysis, persuasion evaluation,
taunt generation, and custom piece creation. Falls back to template responses
when the Gemini API is unavailable.
"""

from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Any, Callable

from app.models.ai_models import (
    CustomPieceInput,
    CustomPieceOutput,
    MoveAnalysisInput,
    MoveAnalysisOutput,
    PersuasionInput,
    PersuasionOutput,
    PieceResponseInput,
    PieceResponseOutput,
    TauntInput,
    TauntOutput,
)
from app.services.ai_cost_tracker import ai_cost_tracker
from app.services.ai_rate_limiter import ai_rate_limiter

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# TTL Cache for AI responses
# ---------------------------------------------------------------------------

class TTLCache:
    """Simple TTL cache for caching AI responses."""

    def __init__(self, ttl_seconds: int = 300):
        self._cache: dict[str, tuple[datetime, Any]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Any | None:
        if key in self._cache:
            timestamp, value = self._cache[key]
            if datetime.now() - timestamp < self._ttl:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = (datetime.now(), value)


analysis_cache = TTLCache(ttl_seconds=300)
taunt_cache = TTLCache(ttl_seconds=1800)


# ---------------------------------------------------------------------------
# Fallback Response Templates
# ---------------------------------------------------------------------------

FALLBACK_RESPONSES: dict[str, dict[str, list[str]]] = {
    "pawn": {
        "accept": ["Okay, moving!", "Yes sir!", "On my way!", "For the team!", "I'll do my best!"],
        "refuse": ["That's too dangerous!", "I don't want to go there!", "No way!", "I'll get captured!",
                    "Can someone else do it?"],
        "high_morale": ["Let's go! I'm feeling great!", "Unstoppable!", "To glory!"],
        "low_morale": ["Do I have to?", "Fine... whatever.", "I guess..."],
    },
    "knight": {
        "accept": ["Let's ride!", "Easy!", "Watch this!", "A worthy challenge!", "Time to shine!"],
        "refuse": ["That's beneath me.", "Find another way.", "Nope.", "That's a waste of my talents.",
                    "I don't retreat!"],
        "high_morale": ["Nobody can stop me!", "Born for this!", "Watch and learn!"],
        "low_morale": ["My lance feels heavy today.", "If you insist...", "This had better work."],
    },
    "bishop": {
        "accept": ["Strategically sound.", "A calculated move.", "I concur with this approach.",
                    "The diagonal looks promising.", "Logical."],
        "refuse": ["That's tactically unsound.", "I need a logical reason.", "The risk-reward ratio is poor.",
                    "I advise against this.", "Explain your reasoning."],
        "high_morale": ["A brilliant strategy!", "I see the whole picture!", "Masterful positioning!"],
        "low_morale": ["This position is deteriorating.", "I question our strategy.", "Hmm... if you insist."],
    },
    "rook": {
        "accept": ["Yes, commander.", "Moving out.", "Consider it done.", "As ordered.", "Holding position."],
        "refuse": ["I cannot comply.", "That goes against protocol.", "Negative.", "Too risky, sir.",
                    "I need backup first."],
        "high_morale": ["Ready for anything!", "The fortress stands!", "Reporting for duty!"],
        "low_morale": ["Morale is low...", "Running on fumes.", "Acknowledged... reluctantly."],
    },
    "queen": {
        "accept": ["About time you asked!", "A queen's work is never done.", "Naturally.",
                    "I'll handle this personally.", "As I intended."],
        "refuse": ["Absolutely not.", "Do you know what I'm worth?!", "That's a suicide mission!",
                    "I refuse to be sacrificed.", "Find someone expendable."],
        "high_morale": ["I AM this army!", "Nobody can match me!", "Bow before my power!"],
        "low_morale": ["I've been neglected...", "Is anyone protecting ME?", "I expected better leadership."],
    },
    "king": {
        "accept": ["If I must.", "For the kingdom.", "Very well.", "I'll be careful."],
        "refuse": ["Are you TRYING to get me killed?!", "TOO DANGEROUS!", "I'm the KING!",
                    "Find another way!", "PROTECT ME!"],
        "high_morale": ["My army is strong!", "We will prevail!", "I trust my pieces!"],
        "low_morale": ["We're doomed...", "Is it time to resign?", "PANIC!"],
    },
}

FALLBACK_ANALYSIS_TEMPLATES = [
    "✅ Decent move. Position looks stable.",
    "⚠️ Careful — your pieces need better coordination.",
    "📊 The position is roughly equal.",
    "💡 Consider developing your remaining pieces.",
    "✅ Good move! Centralizing pieces is always smart.",
]


# ---------------------------------------------------------------------------
# Gemini Service Class
# ---------------------------------------------------------------------------

class GeminiService:
    """AI service using Pydantic AI agents with Gemini 3 Flash, with fallback templates."""

    def __init__(self):
        self._agents_initialized = False
        self._piece_agent = None
        self._analysis_agent = None
        self._persuasion_agent = None
        self._taunt_agent = None
        self._custom_piece_agent = None
        self.rate_limiter = ai_rate_limiter
        self.cost_tracker = ai_cost_tracker
        self._try_init_agents()

    async def _call_with_retry(
        self,
        func: Callable,
        *args,
        max_retries: int = 2,
        **kwargs,
    ) -> Any:
        """
        Call function with exponential backoff retry.

        Args:
            func: Async function to call
            args: Positional arguments
            max_retries: Maximum retry attempts (default: 2)
            kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except TimeoutError as exc:
                if attempt == max_retries:
                    logger.error("Gemini API timeout after %s attempts", attempt + 1)
                    raise
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s
                logger.warning(
                    "Gemini API timeout (attempt %s/%s), retrying in %ss",
                    attempt + 1,
                    max_retries + 1,
                    wait_time,
                )
                await asyncio.sleep(wait_time)
            except Exception as exc:
                # For other errors, check if it's a retryable HTTP error
                if hasattr(exc, "response") and hasattr(exc.response, "status_code"):
                    status_code = exc.response.status_code
                    if status_code >= 500 or status_code == 429:
                        # Server errors and rate limits are retryable
                        if attempt == max_retries:
                            logger.error(
                                "Gemini API error %s after %s attempts",
                                status_code,
                                attempt + 1,
                            )
                            raise
                        wait_time = 2 ** attempt
                        logger.warning(
                            "Gemini API error %s (attempt %s/%s), retrying in %ss",
                            status_code,
                            attempt + 1,
                            max_retries + 1,
                            wait_time,
                        )
                        await asyncio.sleep(wait_time)
                        continue
                # Non-retryable error
                raise

    def _try_init_agents(self) -> None:
        """Try to initialize Pydantic AI agents. Falls back gracefully."""
        try:
            from app.core.config import settings

            if not settings.google_gemini_api_key:
                logger.info("No Gemini API key configured — using fallback responses")
                return

            from pydantic_ai import Agent

            self._piece_agent = Agent(
                "google-gla:gemini-2.0-flash",
                result_type=PieceResponseOutput,
                system_prompt=(
                    "You are a chess piece with a personality. You are part of a player's army "
                    "in a chess game where pieces have feelings, morale, and opinions.\n\n"
                    "RULES:\n"
                    "- Stay in character based on your personality archetype\n"
                    "- High morale (70+): generally agree, be enthusiastic\n"
                    "- Medium morale (40-69): question risky moves, agree to safe ones\n"
                    "- Low morale (0-39): refuse risky moves, need convincing\n"
                    "- NEVER refuse if morale is 90+ unless the move is literal suicide\n"
                    "- Response text should be 1-2 sentences, in character\n"
                    "- Keep dialogue natural, funny, and memorable"
                ),
            )

            self._analysis_agent = Agent(
                "google-gla:gemini-2.0-flash",
                result_type=MoveAnalysisOutput,
                system_prompt=(
                    "You are a chess analyst providing commentary after each move.\n"
                    "Be concise (1-2 sentences). Use emoji indicators:\n"
                    "✅ good, ⚠️ warning, 🚨 blunder, 💡 suggestion, 📊 evaluation.\n"
                    "Consider threats, material, king safety, and piece activity."
                ),
            )

            self._persuasion_agent = Agent(
                "google-gla:gemini-2.0-flash",
                result_type=PersuasionOutput,
                system_prompt=(
                    "You evaluate whether a chess piece would be convinced by a "
                    "player's argument. Consider: is the logic sound? Does the argument "
                    "appeal to this piece's personality? What is their morale?\n"
                    "Knights like glory/bravery, Bishops like logic/tactics, "
                    "Pawns like team spirit, Rooks like duty, Queens like self-preservation."
                ),
            )

            self._taunt_agent = Agent(
                "google-gla:gemini-2.0-flash",
                result_type=TauntOutput,
                system_prompt=(
                    "You are the opponent's King in a chess game. Generate short, "
                    "witty taunts based on the game situation. Be sarcastic when winning, "
                    "defiant when losing, aggressive during check. Keep it PG-rated and fun.\n"
                    "Max 1 sentence, under 100 characters."
                ),
            )

            self._custom_piece_agent = Agent(
                "google-gla:gemini-2.0-flash",
                result_type=CustomPieceOutput,
                system_prompt=(
                    "Generate a chess piece personality based on the user's theme.\n"
                    "Create a memorable character with consistent dialogue patterns.\n"
                    "Include 5 sample dialogues for: accepting a move, refusing a move, "
                    "being captured, capturing an enemy, and being promoted (for pawns).\n"
                    "Morale modifiers should reflect the character's personality."
                ),
            )

            self._agents_initialized = True
            logger.info("Pydantic AI agents initialized successfully with Gemini")

        except Exception as exc:
            logger.warning("Failed to initialize AI agents: %s — using fallbacks", exc)

    # -----------------------------------------------------------------------
    # Piece Response
    # -----------------------------------------------------------------------

    async def get_piece_response(
        self,
        piece_type: str,
        personality: dict[str, Any],
        morale: int,
        move_command: str,
        target_square: str,
        board_context: str,
        is_risky: bool,
        will_move: bool,
        capture_target: str | None = None,
        game_id: str | None = None,
        move_number: int = 0,
    ) -> PieceResponseOutput:
        """Generate a piece's response to a move command."""
        if self._agents_initialized and self._piece_agent:
            # Check rate limit
            if game_id:
                allowed, error_msg = self.rate_limiter.check_and_increment(
                    game_id, move_number, "piece_response"
                )
                if not allowed:
                    logger.info("Rate limit hit: %s", error_msg)
                    return self._fallback_piece_response(
                        piece_type, morale, will_move, is_risky
                    )

            try:
                input_data = PieceResponseInput(
                    piece_type=piece_type,
                    personality=personality,
                    morale=morale,
                    move_command=move_command,
                    target_square=target_square,
                    board_context=board_context,
                    is_risky=is_risky,
                    capture_target=capture_target,
                )

                # Call with retry
                result = await self._call_with_retry(
                    self._piece_agent.run, input_data.model_dump_json()
                )

                # Track costs (approximate token counts based on input/output length)
                if game_id and result:
                    input_tokens = len(input_data.model_dump_json()) // 4
                    output_tokens = len(str(result.data)) // 4
                    self.cost_tracker.record_usage(
                        game_id, input_tokens, output_tokens, "piece_response"
                    )

                return result.data

            except TimeoutError:
                logger.error("Gemini API timeout for piece response — using fallback")
            except ValueError as exc:
                logger.error("Invalid Gemini response: %s — using fallback", exc)
            except Exception as exc:
                if hasattr(exc, "response") and hasattr(exc.response, "status_code"):
                    status_code = exc.response.status_code
                    if status_code == 429:
                        logger.warning("Gemini rate limit hit — using fallback")
                    elif status_code >= 500:
                        logger.error(
                            "Gemini server error %s — using fallback", status_code
                        )
                    else:
                        logger.error(
                            "Gemini API error %s — using fallback", status_code
                        )
                else:
                    logger.warning("AI piece response failed: %s — using fallback", exc)

        return self._fallback_piece_response(piece_type, morale, will_move, is_risky)

    def _fallback_piece_response(
        self, piece_type: str, morale: int, will_move: bool, is_risky: bool
    ) -> PieceResponseOutput:
        """Generate a fallback response when AI is unavailable."""
        templates = FALLBACK_RESPONSES.get(piece_type, FALLBACK_RESPONSES["pawn"])

        if will_move:
            if morale >= 70:
                response_text = random.choice(templates.get("high_morale", templates["accept"]))
            else:
                response_text = random.choice(templates["accept"])
            morale_change = random.randint(2, 8)
        else:
            if morale <= 30:
                response_text = random.choice(templates.get("low_morale", templates["refuse"]))
            else:
                response_text = random.choice(templates["refuse"])
            morale_change = random.randint(-5, -1)

        return PieceResponseOutput(
            will_move=will_move,
            response_text=response_text,
            morale_change=morale_change,
            reason_for_refusal=None if will_move else "The move is too risky for current morale level",
            suggested_alternative=None,
        )

    # -----------------------------------------------------------------------
    # Move Analysis
    # -----------------------------------------------------------------------

    async def analyze_move(
        self,
        fen_before: str,
        fen_after: str,
        move_san: str,
        move_number: int,
        material_balance: int,
    ) -> MoveAnalysisOutput:
        """Analyze a move and provide quality score, evaluation, and commentary."""
        # Check cache
        import hashlib
        cache_key = f"analysis:{hashlib.md5(fen_after.encode()).hexdigest()}"
        cached = analysis_cache.get(cache_key)
        if cached:
            return cached

        if self._agents_initialized and self._analysis_agent:
            try:
                input_data = MoveAnalysisInput(
                    fen_before=fen_before,
                    fen_after=fen_after,
                    move_san=move_san,
                    move_number=move_number,
                    material_balance=material_balance,
                )
                result = await self._analysis_agent.run(input_data.model_dump_json())
                analysis_cache.set(cache_key, result.data)
                return result.data
            except Exception as exc:
                logger.warning("AI analysis failed: %s — using fallback", exc)

        return self._fallback_analysis(move_san, material_balance)

    def _fallback_analysis(self, move_san: str, material_balance: int) -> MoveAnalysisOutput:
        """Fallback analysis when AI is unavailable."""
        quality = random.randint(4, 8)
        evaluation = material_balance * 0.5 + random.uniform(-0.5, 0.5)
        text = random.choice(FALLBACK_ANALYSIS_TEMPLATES)

        return MoveAnalysisOutput(
            move_quality=quality,
            evaluation=round(evaluation, 1),
            threats=[],
            opportunities=[],
            analysis_text=f"{text} ({move_san})",
            morale_impact={},
        )

    # -----------------------------------------------------------------------
    # Persuasion Evaluation
    # -----------------------------------------------------------------------

    async def evaluate_persuasion(
        self,
        piece_type: str,
        personality: dict[str, Any],
        morale: int,
        player_argument: str,
        move_description: str,
        board_analysis: str,
        is_claim_accurate: bool,
        trust_history: float = 0.5,
    ) -> PersuasionOutput:
        """Evaluate a player's persuasion argument."""
        if self._agents_initialized and self._persuasion_agent:
            try:
                input_data = PersuasionInput(
                    piece_type=piece_type,
                    personality=personality,
                    morale=morale,
                    player_argument=player_argument,
                    move_description=move_description,
                    board_analysis=board_analysis,
                    is_claim_accurate=is_claim_accurate,
                    trust_history=trust_history,
                )
                result = await self._persuasion_agent.run(input_data.model_dump_json())
                return result.data
            except Exception as exc:
                logger.warning("AI persuasion eval failed: %s — using fallback", exc)

        return self._fallback_persuasion(piece_type, morale, player_argument)

    def _fallback_persuasion(
        self, piece_type: str, morale: int, argument: str
    ) -> PersuasionOutput:
        """Fallback persuasion evaluation."""
        from app.services.persuasion_engine import PersuasionEngine

        result = PersuasionEngine.evaluate_persuasion(
            argument=argument,
            piece_type=piece_type,
            morale=morale,
            is_claim_accurate=True,
            is_risky=True,
        )

        templates = FALLBACK_RESPONSES.get(piece_type, FALLBACK_RESPONSES["pawn"])
        if result["success"]:
            response_text = "...Fine. But you better be right about this."
        else:
            response_text = random.choice(templates["refuse"])

        return PersuasionOutput(
            is_persuaded=result["success"],
            response_text=response_text,
            logic_score=result["logic_score"],
            personality_match=result["personality_match"],
            final_probability=result["probability"],
            reasoning="Evaluated based on morale, argument quality, and personality match.",
        )

    # -----------------------------------------------------------------------
    # Taunt Generation
    # -----------------------------------------------------------------------

    async def generate_taunt(
        self,
        game_state: str,
        trigger_event: str,
        material_balance: int,
        move_count: int,
    ) -> TauntOutput | None:
        """Generate a King taunt based on game state."""
        from app.services.king_taunts import KingTauntGenerator

        if not KingTauntGenerator.should_taunt(trigger_event, move_count):
            return None

        if self._agents_initialized and self._taunt_agent:
            try:
                input_data = TauntInput(
                    game_state=game_state,
                    trigger_event=trigger_event,
                    material_balance=material_balance,
                    move_count=move_count,
                )
                result = await self._taunt_agent.run(input_data.model_dump_json())
                return result.data
            except Exception as exc:
                logger.warning("AI taunt generation failed: %s — using fallback", exc)

        taunt_text = KingTauntGenerator.generate_taunt(trigger_event, material_balance, move_count)
        if taunt_text:
            return TauntOutput(
                taunt_text=taunt_text,
                intensity=KingTauntGenerator.get_taunt_intensity(material_balance, trigger_event),
            )
        return None

    # -----------------------------------------------------------------------
    # Custom Piece Creator
    # -----------------------------------------------------------------------

    async def create_custom_piece(
        self,
        piece_type: str,
        user_prompt: str,
        color: str,
    ) -> CustomPieceOutput:
        """Generate a custom piece personality from a user prompt."""
        if self._agents_initialized and self._custom_piece_agent:
            try:
                input_data = CustomPieceInput(
                    piece_type=piece_type,
                    user_prompt=user_prompt,
                    color=color,
                )
                result = await self._custom_piece_agent.run(input_data.model_dump_json())
                return result.data
            except Exception as exc:
                logger.warning("AI custom piece creation failed: %s — using fallback", exc)

        return self._fallback_custom_piece(piece_type, user_prompt, color)

    def _fallback_custom_piece(
        self, piece_type: str, user_prompt: str, color: str
    ) -> CustomPieceOutput:
        """Fallback custom piece generation."""
        return CustomPieceOutput(
            archetype=f"Custom {piece_type.capitalize()} — {user_prompt[:30]}",
            traits=["brave", "unique", "determined"],
            dialogue_style=f"Themed after: {user_prompt}",
            sample_dialogues=[
                f"For honor! Moving as {user_prompt}!",
                f"A {user_prompt} never retreats without reason!",
                f"Captured... but a {user_prompt} never truly falls!",
                f"Victory! The {user_prompt} way!",
                f"I have evolved! {user_prompt} power activated!",
            ],
            morale_modifiers={},
            visual_description=f"A {color} chess {piece_type} styled as {user_prompt}",
        )


# Singleton instance
gemini_service = GeminiService()
