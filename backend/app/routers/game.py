"""Game router — CRUD, move commands, persuasion, resign, draw.

Uses Supabase for persistent game storage.
Players are identified by a session_id header (X-Session-Id).
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, status

from app.db import store
from app.models.game_models import (
    BoardState,
    CommandRequest,
    CommandResponse,
    CreateGameRequest,
    DrawRespondRequest,
    GameResponse,
    GameSettings,
    JoinGameRequest,
    MoraleChange,
    MoveAnalysis,
    MoveData,
    PersuasionEvaluation,
    PersuasionRequest,
    PersuasionResponse,
    PieceResponseData,
    PieceState,
    PiecePersonality,
    PlayerSummary,
)
from app.data.piece_templates import get_piece_accept_text, get_piece_refuse_text
from app.services.chess_engine import ChessEngine
from app.services.morale_calculator import MoraleCalculator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/games", tags=["game-actions"])


def _get_session(x_session_id: str | None) -> str:
    """Return the session id, creating one if missing."""
    return x_session_id or str(uuid4())


def _build_game_response(game: dict[str, Any]) -> GameResponse:
    """Build a GameResponse from in-memory game data."""
    pieces = store.get_game_pieces(game["id"])

    white_player = None
    if game.get("white_player_id") and game["white_player_id"] != "ai":
        white_player = PlayerSummary(
            id=game["white_player_id"],
            username=f"Player-{game['white_player_id'][:6]}",
            avatar_url=None,
        )

    black_player = None
    if game.get("black_player_id") and game["black_player_id"] != "ai":
        black_player = PlayerSummary(
            id=game["black_player_id"],
            username=f"Player-{game['black_player_id'][:6]}",
            avatar_url=None,
        )
    elif game.get("black_player_id") == "ai":
        black_player = PlayerSummary(id="ai", username="AI Opponent", avatar_url=None)

    return GameResponse(
        id=game["id"],
        status=game["status"],
        game_mode=game["game_mode"],
        template=game["template"],
        share_code=game["share_code"],
        fen=game["fen"],
        turn=game["turn"],
        white_player=white_player,
        black_player=black_player,
        pieces=[
            PieceState(
                id=p["id"],
                color=p["color"],
                piece_type=p["piece_type"],
                square=p.get("square"),
                morale=p.get("morale", 70),
                personality=PiecePersonality(**(p.get("personality") or {})),
                is_captured=p.get("is_captured", False),
            )
            for p in pieces
        ],
        settings=GameSettings(**(game.get("settings") or {})),
        created_at=game["created_at"],
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("", response_model=GameResponse, tags=["games"])
async def create_game(
    request: CreateGameRequest,
    x_session_id: str | None = Header(default=None),
):
    """Create a new game. No login required."""
    session_id = _get_session(x_session_id)

    game = store.create_game(
        session_id=session_id,
        game_mode=request.game_mode,
        template=request.template,
        settings=(request.settings or GameSettings()).model_dump() if request.settings else None,
    )

    response = _build_game_response(game)
    return response


@router.get("/{game_id}", response_model=GameResponse, tags=["games"])
async def get_game(game_id: str):
    """Get the current state of a game."""
    game = store.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail={"error_code": "GAME_NOT_FOUND", "message": "Game not found"})
    return _build_game_response(game)


@router.post("/join-by-code", response_model=GameResponse, tags=["games"])
async def join_by_share_code(
    request: JoinGameRequest,
    x_session_id: str | None = Header(default=None),
):
    """Join a game via share code."""
    session_id = _get_session(x_session_id)

    game = store.get_game_by_share_code(request.share_code)
    if not game:
        raise HTTPException(status_code=404, detail={"error_code": "GAME_NOT_FOUND", "message": "Invalid share code"})

    if game["status"] != "waiting":
        raise HTTPException(status_code=400, detail={"error_code": "GAME_FULL", "message": "Game is not accepting players"})

    if game["white_player_id"] == session_id:
        raise HTTPException(status_code=400, detail={"error_code": "GAME_FULL", "message": "Cannot join your own game"})

    store.update_game(game["id"], {
        "black_player_id": session_id,
        "status": "active",
    })

    store.add_message(game["id"], "system", "System", "Opponent joined! The game begins. White moves first.")

    return _build_game_response(store.get_game(game["id"]))


@router.post("/{game_id}/join", response_model=GameResponse, tags=["games"])
async def join_game(
    game_id: str,
    request: JoinGameRequest,
    x_session_id: str | None = Header(default=None),
):
    """Join a game via share code (by game ID route)."""
    session_id = _get_session(x_session_id)

    game = store.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail={"error_code": "GAME_NOT_FOUND", "message": "Game not found"})

    if game["share_code"] != request.share_code:
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_CODE", "message": "Share code mismatch"})

    if game["status"] != "waiting":
        raise HTTPException(status_code=400, detail={"error_code": "GAME_FULL", "message": "Game is not accepting players"})

    if game["white_player_id"] == session_id:
        raise HTTPException(status_code=400, detail={"error_code": "GAME_FULL", "message": "Cannot join your own game"})

    store.update_game(game["id"], {
        "black_player_id": session_id,
        "status": "active",
    })

    store.add_message(game["id"], "system", "System", "Opponent joined! The game begins. White moves first.")

    return _build_game_response(store.get_game(game["id"]))


@router.post("/{game_id}/command", response_model=CommandResponse)
async def issue_command(
    game_id: str,
    request: CommandRequest,
    x_session_id: str | None = Header(default=None),
):
    """Issue a move command to a piece."""
    session_id = _get_session(x_session_id)

    game = store.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail={"error_code": "GAME_NOT_FOUND", "message": "Game not found"})

    if game["status"] != "active":
        raise HTTPException(status_code=400, detail={"error_code": "GAME_ENDED", "message": "Game is not active"})

    # Check turn
    is_white = game["white_player_id"] == session_id
    is_black = game.get("black_player_id") == session_id
    current_turn = game["turn"]

    if (current_turn == "white" and not is_white) or (current_turn == "black" and not is_black):
        raise HTTPException(status_code=400, detail={"error_code": "NOT_YOUR_TURN", "message": "It's not your turn"})

    # Get the piece
    piece = store.get_piece(request.piece_id)
    if not piece:
        raise HTTPException(status_code=404, detail={"error_code": "PIECE_NOT_FOUND", "message": "Piece not found"})

    if piece["is_captured"]:
        raise HTTPException(status_code=400, detail={"error_code": "PIECE_CAPTURED", "message": "Piece is captured"})

    expected_color = "white" if is_white else "black"
    if piece["color"] != expected_color:
        raise HTTPException(status_code=400, detail={"error_code": "FORBIDDEN", "message": "Not your piece"})

    # Validate move
    engine = ChessEngine(game["fen"])
    validation = engine.validate_move(piece["square"], request.target_square)

    if not validation["legal"]:
        raise HTTPException(status_code=400, detail={"error_code": "INVALID_MOVE", "message": validation.get("error", "Illegal move")})

    # Check morale
    morale = piece.get("morale", 70)
    piece_type = piece["piece_type"]
    is_risky = validation.get("is_risky", False)
    will_move = MoraleCalculator.will_piece_obey(morale, is_risky, piece_type)

    # Player command in chat
    player_name = f"Player-{session_id[:6]}"
    store.add_message(
        game_id, "player_command", player_name,
        request.message or f"@{piece_type.capitalize()}-{piece['square']} move to {request.target_square}",
        metadata={"piece_id": request.piece_id, "target_square": request.target_square},
        sender_id=session_id,
    )

    # AI piece response (use fallback — no Gemini needed for demo)
    if will_move:
        response_text = get_piece_accept_text(piece_type, request.target_square)
        morale_change = 3
    else:
        response_text = get_piece_refuse_text(piece_type, morale)
        morale_change = -2

    msg_type = "piece_response" if will_move else "piece_refusal"
    store.add_message(game_id, msg_type, f"{piece_type.capitalize()}-{piece['square']}", response_text,
                      metadata={"piece_id": request.piece_id, "morale": morale, "will_move": will_move})

    morale_changes: list[MoraleChange] = []
    analysis_result: MoveAnalysis | None = None
    king_taunt_text: str | None = None
    board_state = BoardState(fen=game["fen"], turn=game["turn"], is_check=engine.is_check)

    if will_move:
        # Execute move — capture original square before updating piece position
        original_square = piece["square"]
        move_result = engine.make_move_from_squares(piece["square"], request.target_square)
        new_fen = move_result["fen_after"]
        new_turn = "black" if current_turn == "white" else "white"

        move_number = store.get_move_count(game_id) + 1
        store.add_move(game_id, {
            "game_id": game_id,
            "piece_id": piece["id"],
            "player_id": session_id,
            "move_number": move_number,
            "from_square": piece["square"],
            "to_square": request.target_square,
            "san": validation["san"],
            "fen_after": new_fen,
        })

        # Update piece position
        store.update_piece(piece["id"], {"square": request.target_square})

        # Handle capture
        if validation.get("is_capture"):
            for cp in store.get_game_pieces(game_id):
                if cp["square"] == request.target_square and cp["id"] != piece["id"] and not cp["is_captured"]:
                    store.update_piece(cp["id"], {"is_captured": True, "square": None})
                    break

        # Update morale
        new_morale = MoraleCalculator.apply_morale_change(morale, morale_change)
        store.update_piece(piece["id"], {"morale": new_morale})

        morale_changes.append(MoraleChange(
            piece_id=piece["id"],
            event_type="capture_enemy" if validation.get("is_capture") else "good_position",
            change=morale_change,
            morale_after=new_morale,
            description=MoraleCalculator.generate_morale_description(
                "capture_enemy" if validation.get("is_capture") else "good_position",
                piece_type, morale_change, new_morale,
            ),
        ))

        # Check game end
        game_result = engine.get_game_result()
        game_update: dict[str, Any] = {"fen": new_fen, "turn": new_turn}
        if game_result:
            game_update["status"] = "completed"
            game_update["result"] = game_result
        store.update_game(game_id, game_update)

        board_state = BoardState(
            fen=new_fen,
            turn=new_turn,
            is_check=engine.is_check,
            is_checkmate=engine.is_checkmate,
            is_stalemate=engine.is_stalemate,
            last_move=MoveData(
                from_square=original_square,
                to_square=request.target_square,
                san=validation["san"],
                piece_type=piece_type,
            ),
        )

        # Simple analysis message
        if validation.get("is_capture"):
            analysis_text = f"Captured piece at {request.target_square}. Material advantage shifting."
        else:
            analysis_text = f"Solid positional move: {validation['san']}."

        store.add_message(game_id, "ai_analysis", "AI Analyst", analysis_text,
                          metadata={"move_quality": 7, "evaluation": 0.2})

        analysis_result = MoveAnalysis(
            move_quality=7, evaluation=0.2,
            threats=[], opportunities=[],
            analysis_text=analysis_text,
        )

        # King taunt (template-based)
        from app.services.king_taunts import KingTauntGenerator
        trigger = "piece_captured" if validation.get("is_capture") else "great_move"
        if engine.is_check:
            trigger = "check"
        taunt = KingTauntGenerator.generate_taunt(
            trigger, engine.get_material_balance(), move_number,
            piece_type,
        )
        if taunt:
            king_taunt_text = taunt
            store.add_message(game_id, "king_taunt", "Opponent King ♚", taunt,
                              metadata={"intensity": "medium"})

    new_morale_value = MoraleCalculator.apply_morale_change(morale, morale_change)

    return CommandResponse(
        success=True,
        move_executed=will_move,
        piece_response=PieceResponseData(
            will_move=will_move,
            response_text=response_text,
            morale_before=morale,
            morale_after=new_morale_value,
            reason_for_refusal=None if will_move else response_text,
        ),
        board_state=board_state,
        morale_changes=morale_changes,
        analysis=analysis_result,
        king_taunt=king_taunt_text,
    )


@router.post("/{game_id}/persuade", response_model=PersuasionResponse)
async def persuade_piece(
    game_id: str,
    request: PersuasionRequest,
    x_session_id: str | None = Header(default=None),
):
    """Submit a persuasion attempt."""
    session_id = _get_session(x_session_id)
    game = store.get_game(game_id)
    if not game or game["status"] != "active":
        raise HTTPException(status_code=400, detail={"error_code": "GAME_ENDED", "message": "Game not active"})

    piece = store.get_piece(request.piece_id)
    if not piece:
        raise HTTPException(status_code=404, detail={"error_code": "PIECE_NOT_FOUND", "message": "Piece not found"})

    engine = ChessEngine(game["fen"])
    validation = engine.validate_move(piece["square"], request.target_square)
    is_risky = validation.get("is_risky", False)

    store.add_message(game_id, "persuasion_attempt", f"Player-{session_id[:6]}", request.argument,
                      metadata={"piece_id": request.piece_id, "is_voice": request.is_voice}, sender_id=session_id)

    # Evaluate persuasion
    from app.services.persuasion_engine import PersuasionEngine

    pe_result = PersuasionEngine.evaluate_persuasion(
        argument=request.argument,
        piece_type=piece["piece_type"],
        morale=piece.get("morale", 70),
        is_claim_accurate=validation.get("legal", False),
        is_risky=is_risky,
        is_check=engine.is_check,
        material_balance=engine.get_material_balance(),
        move_count=store.get_move_count(game_id),
    )

    import random
    success = random.random() < pe_result["probability"]

    if success:
        response_text = f"*sighs* Fine, you make a good point. I'll move to {request.target_square}."
    else:
        response_text = f"Nope, still not convinced. Try harder, commander!"

    store.add_message(game_id, "persuasion_result", f"{piece['piece_type'].capitalize()}-{piece['square']}", response_text,
                      metadata={"success": success, "probability": pe_result["probability"]})

    store.add_persuasion(game_id, {
        "game_id": game_id,
        "piece_id": request.piece_id,
        "player_id": session_id,
        "argument_text": request.argument,
        "is_voice": request.is_voice,
        "success": success,
        "success_probability": pe_result["probability"],
        "piece_response": response_text,
        "evaluation": pe_result,
    })

    board_state = None

    if success and validation.get("legal"):
        original_square = piece["square"]
        move_result = engine.make_move_from_squares(piece["square"], request.target_square)
        new_fen = move_result["fen_after"]
        new_turn = "black" if game["turn"] == "white" else "white"

        move_number = store.get_move_count(game_id) + 1
        store.add_move(game_id, {
            "game_id": game_id,
            "piece_id": piece["id"],
            "player_id": session_id,
            "move_number": move_number,
            "from_square": piece["square"],
            "to_square": request.target_square,
            "san": validation["san"],
            "fen_after": new_fen,
        })

        store.update_piece(piece["id"], {"square": request.target_square})

        if validation.get("is_capture"):
            for cp in store.get_game_pieces(game_id):
                if cp["square"] == request.target_square and cp["id"] != piece["id"] and not cp["is_captured"]:
                    store.update_piece(cp["id"], {"is_captured": True, "square": None})
                    break

        new_morale = MoraleCalculator.apply_morale_change(piece.get("morale", 70), 5)
        store.update_piece(piece["id"], {"morale": new_morale})

        game_result = engine.get_game_result()
        game_update: dict[str, Any] = {"fen": new_fen, "turn": new_turn}
        if game_result:
            game_update["status"] = "completed"
            game_update["result"] = game_result
        store.update_game(game_id, game_update)

        board_state = BoardState(
            fen=new_fen,
            turn=new_turn,
            is_check=engine.is_check,
            is_checkmate=engine.is_checkmate,
            is_stalemate=engine.is_stalemate,
            last_move=MoveData(
                from_square=original_square,
                to_square=request.target_square,
                san=validation["san"],
                piece_type=piece["piece_type"],
            ),
        )

    return PersuasionResponse(
        success=success,
        probability=pe_result["probability"],
        piece_response=response_text,
        move_executed=success and validation.get("legal", False),
        board_state=board_state,
        evaluation=PersuasionEvaluation(
            logic_score=pe_result["logic_score"],
            personality_match=pe_result["personality_match"],
            morale_modifier=pe_result["morale_modifier"],
            trust_modifier=pe_result["trust_modifier"],
            urgency_factor=pe_result["urgency_factor"],
            total_probability=pe_result["probability"],
        ),
    )


@router.post("/{game_id}/resign")
async def resign_game(
    game_id: str,
    x_session_id: str | None = Header(default=None),
):
    """Resign from a game."""
    session_id = _get_session(x_session_id)
    game = store.get_game(game_id)
    if not game or game["status"] != "active":
        raise HTTPException(status_code=400, detail={"error_code": "GAME_ENDED", "message": "Game not active"})

    is_white = game["white_player_id"] == session_id
    result = "black_wins" if is_white else "white_wins"

    store.update_game(game_id, {"status": "completed", "result": result})
    store.add_message(game_id, "system", "System",
                      f"{'White' if is_white else 'Black'} resigned. {result.replace('_', ' ').title()}!")

    return {"success": True, "result": result}


@router.post("/{game_id}/draw-offer")
async def offer_draw(
    game_id: str,
    x_session_id: str | None = Header(default=None),
):
    """Offer a draw."""
    session_id = _get_session(x_session_id)
    game = store.get_game(game_id)
    if not game or game["status"] != "active":
        raise HTTPException(status_code=400, detail={"error_code": "GAME_ENDED", "message": "Game not active"})

    store.add_message(game_id, "system", "System", "Draw offered. Waiting for opponent's response...",
                      metadata={"draw_offered_by": session_id}, sender_id=session_id)
    return {"success": True, "message": "Draw offered"}


@router.post("/{game_id}/draw-respond")
async def respond_to_draw(
    game_id: str,
    request: DrawRespondRequest,
):
    """Accept or decline a draw offer."""
    game = store.get_game(game_id)
    if not game or game["status"] != "active":
        raise HTTPException(status_code=400, detail={"error_code": "GAME_ENDED", "message": "Game not active"})

    if request.accept:
        store.update_game(game_id, {"status": "completed", "result": "draw"})
        store.add_message(game_id, "system", "System", "Draw accepted! The game ends in a draw.")
        return {"success": True, "result": "draw"}
    else:
        store.add_message(game_id, "system", "System", "Draw declined. The game continues.")
        return {"success": True, "result": "declined"}


@router.get("/{game_id}/moves", tags=["games"])
async def get_moves(game_id: str):
    """Get move history for a game."""
    moves = store.get_moves(game_id)
    return {"moves": moves}
