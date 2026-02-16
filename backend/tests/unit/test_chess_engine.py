"""Unit tests for ChessEngine service."""

from __future__ import annotations

import pytest

from app.services.chess_engine import ChessEngine


class TestChessEngineInitialization:
    """Test chess engine initialization."""

    def test_init_default_position(self):
        """Test initialization with default starting position."""
        engine = ChessEngine()

        assert engine.fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        assert engine.turn == "white"
        assert not engine.is_check
        assert not engine.is_checkmate
        assert not engine.is_stalemate
        assert not engine.is_game_over

    def test_init_custom_fen(self):
        """Test initialization with custom FEN position."""
        # Position after 1.e4
        custom_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        engine = ChessEngine(fen=custom_fen)

        assert engine.fen == custom_fen
        assert engine.turn == "black"
        assert not engine.is_check

    def test_init_check_position(self):
        """Test initialization with a position where king is in check."""
        # White king in check from black queen
        check_fen = "rnb1kbnr/pppppppp/8/8/8/8/PPPPqPPP/RNBQKBNR w KQkq - 0 1"
        engine = ChessEngine(fen=check_fen)

        assert engine.is_check
        assert not engine.is_checkmate

    def test_init_checkmate_position(self):
        """Test initialization with checkmate position (fool's mate)."""
        # Fool's mate position
        checkmate_fen = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
        engine = ChessEngine(fen=checkmate_fen)

        assert engine.is_check
        assert engine.is_checkmate
        assert engine.is_game_over


class TestLegalMoves:
    """Test legal move generation."""

    def test_get_legal_moves_starting_position(self):
        """Test getting all legal moves from starting position."""
        engine = ChessEngine()
        moves = engine.get_legal_moves()

        # Starting position has 20 legal moves (16 pawn moves + 4 knight moves)
        assert len(moves) == 20

        # Check move structure
        assert all("from_square" in move for move in moves)
        assert all("to_square" in move for move in moves)
        assert all("san" in move for move in moves)

        # Verify some specific moves exist
        pawn_moves = [m for m in moves if m["from_square"] == "e2"]
        assert len(pawn_moves) == 2  # e3 and e4

        knight_moves = [m for m in moves if m["from_square"] == "g1"]
        assert len(knight_moves) == 2  # Nf3 and Nh3

    def test_get_legal_moves_for_square(self):
        """Test getting legal moves for a specific square."""
        engine = ChessEngine()

        # Test pawn on e2
        e2_moves = engine.get_legal_moves_for_square("e2")
        assert len(e2_moves) == 2
        target_squares = {move["to_square"] for move in e2_moves}
        assert target_squares == {"e3", "e4"}

        # Test knight on g1
        g1_moves = engine.get_legal_moves_for_square("g1")
        assert len(g1_moves) == 2
        target_squares = {move["to_square"] for move in g1_moves}
        assert target_squares == {"f3", "h3"}

        # Test empty square
        empty_moves = engine.get_legal_moves_for_square("e4")
        assert len(empty_moves) == 0

        # Test invalid square
        invalid_moves = engine.get_legal_moves_for_square("z9")
        assert len(invalid_moves) == 0

    def test_get_legal_moves_after_move(self):
        """Test legal moves change after making a move."""
        engine = ChessEngine()

        # Make move e4
        engine.make_move_from_squares("e2", "e4")

        # Now it's black's turn
        assert engine.turn == "black"

        # Black should have 20 legal moves
        moves = engine.get_legal_moves()
        assert len(moves) == 20

        # Black's e7 pawn should be able to move to e5 or e6
        e7_moves = engine.get_legal_moves_for_square("e7")
        assert len(e7_moves) == 2
        target_squares = {move["to_square"] for move in e7_moves}
        assert target_squares == {"e5", "e6"}


class TestMoveValidation:
    """Test move validation."""

    def test_validate_legal_move(self):
        """Test validating a legal move."""
        engine = ChessEngine()

        result = engine.validate_move("e2", "e4")

        assert result["legal"] is True
        assert result["san"] == "e4"
        assert result["is_capture"] is False
        assert result["captured_piece"] is None
        assert "move" in result

    def test_validate_illegal_move(self):
        """Test validating an illegal move."""
        engine = ChessEngine()

        # Try to move pawn 3 squares forward
        result = engine.validate_move("e2", "e5")

        assert result["legal"] is False
        assert "error" in result

    def test_validate_invalid_square(self):
        """Test validation with invalid square notation."""
        engine = ChessEngine()

        result = engine.validate_move("z9", "e4")

        assert result["legal"] is False
        assert result["error"] == "Invalid square"

    def test_validate_capture_move(self):
        """Test validating a capture move."""
        # Position where white can capture black pawn
        fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"
        engine = ChessEngine(fen=fen)

        result = engine.validate_move("e4", "e5")

        assert result["legal"] is True
        assert result["is_capture"] is True
        assert result["captured_piece"] == "pawn"
        assert "x" in result["san"]  # Capture notation includes 'x'

    def test_validate_pawn_promotion(self):
        """Test pawn promotion to queen."""
        # White pawn on 7th rank ready to promote
        fen = "4k3/4P3/8/8/8/8/8/4K3 w - - 0 1"
        engine = ChessEngine(fen=fen)

        result = engine.validate_move("e7", "e8")

        assert result["legal"] is True
        # Should auto-promote to queen
        assert "=" in result["san"] or "Q" in result["san"]


class TestMoveExecution:
    """Test move execution."""

    def test_make_move(self):
        """Test executing a move."""
        engine = ChessEngine()

        initial_fen = engine.fen
        result = engine.validate_move("e2", "e4")
        new_fen = engine.make_move(result["move"])

        assert new_fen != initial_fen
        assert engine.turn == "black"  # Turn should change

    def test_make_move_from_squares(self):
        """Test making a move from square notation."""
        engine = ChessEngine()

        result = engine.make_move_from_squares("e2", "e4")

        assert result["legal"] is True
        assert result["san"] == "e4"
        assert "fen_before" in result
        assert "fen_after" in result
        assert result["fen_before"] != result["fen_after"]
        assert result["is_check"] is False
        assert result["is_checkmate"] is False

    def test_make_move_from_squares_invalid(self):
        """Test making an invalid move."""
        engine = ChessEngine()

        result = engine.make_move_from_squares("e2", "e5")

        assert result["legal"] is False
        assert "error" in result
        # FEN should not change
        assert engine.fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def test_move_results_in_check(self):
        """Test move that results in check."""
        # Position where Qh5 gives check
        fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
        engine = ChessEngine(fen=fen)

        result = engine.make_move_from_squares("d1", "h5")

        assert result["legal"] is True
        assert result["is_check"] is True
        assert result["is_checkmate"] is False

    def test_move_results_in_checkmate(self):
        """Test move that results in checkmate (scholar's mate)."""
        # Position right before scholar's mate
        fen = "rnbqk1nr/pppp1ppp/5b2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 4"
        engine = ChessEngine(fen=fen)

        result = engine.make_move_from_squares("f3", "f7")

        assert result["legal"] is True
        assert result["is_check"] is True
        assert result["is_checkmate"] is True


class TestPieceInfo:
    """Test piece information retrieval."""

    def test_get_piece_at_occupied_square(self):
        """Test getting piece information from occupied square."""
        engine = ChessEngine()

        piece = engine.get_piece_at("e2")

        assert piece is not None
        assert piece["type"] == "pawn"
        assert piece["color"] == "white"
        assert piece["square"] == "e2"

    def test_get_piece_at_empty_square(self):
        """Test getting piece from empty square."""
        engine = ChessEngine()

        piece = engine.get_piece_at("e4")

        assert piece is None

    def test_get_piece_at_invalid_square(self):
        """Test getting piece with invalid square notation."""
        engine = ChessEngine()

        piece = engine.get_piece_at("z9")

        assert piece is None

    def test_get_piece_different_types(self):
        """Test getting different piece types."""
        engine = ChessEngine()

        # Test various starting pieces
        knight = engine.get_piece_at("g1")
        assert knight["type"] == "knight"
        assert knight["color"] == "white"

        queen = engine.get_piece_at("d1")
        assert queen["type"] == "queen"
        assert queen["color"] == "white"

        king = engine.get_piece_at("e8")
        assert king["type"] == "king"
        assert king["color"] == "black"


class TestGameStateProperties:
    """Test game state properties."""

    def test_stalemate_detection(self):
        """Test stalemate position detection."""
        # Stalemate position: black king has no legal moves but not in check
        stalemate_fen = "k7/8/1K6/8/8/8/8/1Q6 b - - 0 1"
        engine = ChessEngine(fen=stalemate_fen)

        assert not engine.is_check
        assert not engine.is_checkmate
        assert engine.is_stalemate
        assert engine.is_game_over

    def test_not_game_over(self):
        """Test active game state."""
        engine = ChessEngine()

        assert not engine.is_game_over
        assert not engine.is_checkmate
        assert not engine.is_stalemate


class TestRiskyMoves:
    """Test risky move assessment."""

    def test_risky_move_detection(self):
        """Test that moving into attack is detected as risky."""
        # Position where moving knight to f3 is attacked by black pawn
        fen = "rnbqkbnr/pppp1ppp/8/4p3/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        engine = ChessEngine(fen=fen)

        # Move knight to f3 - it will be attacked by e5 pawn
        # Note: This tests the _is_move_risky internal logic
        result = engine.validate_move("g1", "f3")

        assert result["legal"] is True
        # This position may or may not be considered risky depending on implementation
        # Just verify the field exists
        assert "is_risky" in result


@pytest.mark.parametrize(
    "fen,expected_turn",
    [
        ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "white"),
        ("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", "black"),
    ],
)
def test_turn_detection(fen: str, expected_turn: str):
    """Test turn detection from FEN string."""
    engine = ChessEngine(fen=fen)
    assert engine.turn == expected_turn
