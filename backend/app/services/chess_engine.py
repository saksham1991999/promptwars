"""Chess engine service wrapping python-chess for move validation and analysis."""

from __future__ import annotations

import logging
from typing import Any

import chess

logger = logging.getLogger(__name__)

# Piece type mapping from python-chess to our string types
PIECE_TYPE_MAP = {
    chess.PAWN: "pawn",
    chess.KNIGHT: "knight",
    chess.BISHOP: "bishop",
    chess.ROOK: "rook",
    chess.QUEEN: "queen",
    chess.KING: "king",
}

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}


class ChessEngine:
    """Wraps python-chess for move validation, state management, and analysis."""

    def __init__(self, fen: str | None = None):
        """Initialize with optional FEN string, defaults to starting position."""
        self.board = chess.Board(fen) if fen else chess.Board()

    @property
    def fen(self) -> str:
        return self.board.fen()

    @property
    def turn(self) -> str:
        return "white" if self.board.turn == chess.WHITE else "black"

    @property
    def is_check(self) -> bool:
        return self.board.is_check()

    @property
    def is_checkmate(self) -> bool:
        return self.board.is_checkmate()

    @property
    def is_stalemate(self) -> bool:
        return self.board.is_stalemate()

    @property
    def is_game_over(self) -> bool:
        return self.board.is_game_over()

    def get_legal_moves(self) -> list[dict[str, str]]:
        """Get all legal moves as a list of {from_square, to_square, san}."""
        moves = []
        for move in self.board.legal_moves:
            san = self.board.san(move)
            moves.append({
                "from_square": chess.square_name(move.from_square),
                "to_square": chess.square_name(move.to_square),
                "san": san,
            })
        return moves

    def get_legal_moves_for_square(self, square_name: str) -> list[dict[str, str]]:
        """Get legal moves for a specific piece/square."""
        try:
            square = chess.parse_square(square_name)
        except ValueError:
            return []

        moves = []
        for move in self.board.legal_moves:
            if move.from_square == square:
                san = self.board.san(move)
                moves.append({
                    "from_square": square_name,
                    "to_square": chess.square_name(move.to_square),
                    "san": san,
                })
        return moves

    def validate_move(self, from_square: str, to_square: str) -> dict[str, Any]:
        """Validate if a move is legal.

        Returns dict with ``legal``, ``move`` (chess.Move), ``san``,
        ``is_capture``, ``captured_piece``, ``is_risky`` keys.
        """
        try:
            from_sq = chess.parse_square(from_square)
            to_sq = chess.parse_square(to_square)
        except ValueError:
            return {"legal": False, "error": "Invalid square"}

        # Check for promotion
        piece = self.board.piece_at(from_sq)
        promotion = None
        if piece and piece.piece_type == chess.PAWN:
            # Auto-promote to queen
            back_rank = 7 if self.board.turn == chess.WHITE else 0
            if chess.square_rank(to_sq) == back_rank:
                promotion = chess.QUEEN

        move = chess.Move(from_sq, to_sq, promotion=promotion)

        if move not in self.board.legal_moves:
            return {"legal": False, "error": "Illegal move"}

        # Check if it's a capture
        is_capture = self.board.is_capture(move)
        captured_piece = None
        if is_capture:
            captured = self.board.piece_at(to_sq)
            if captured:
                captured_piece = PIECE_TYPE_MAP.get(captured.piece_type, "unknown")

        # Assess risk: will the piece be attacked at the target square?
        is_risky = self._is_move_risky(move)

        san = self.board.san(move)

        return {
            "legal": True,
            "move": move,
            "san": san,
            "is_capture": is_capture,
            "captured_piece": captured_piece,
            "is_risky": is_risky,
        }

    def make_move(self, move: chess.Move) -> str:
        """Execute a move and return the new FEN."""
        self.board.push(move)
        return self.fen

    def make_move_from_squares(self, from_square: str, to_square: str) -> dict[str, Any]:
        """Validate and execute a move, returning result info."""
        result = self.validate_move(from_square, to_square)
        if not result["legal"]:
            return result

        result["fen_before"] = self.fen
        self.make_move(result["move"])
        result["fen_after"] = self.fen
        result["is_check"] = self.is_check
        result["is_checkmate"] = self.is_checkmate
        result["is_stalemate"] = self.is_stalemate
        return result

    def get_piece_at(self, square_name: str) -> dict[str, str] | None:
        """Get piece info at a given square."""
        try:
            square = chess.parse_square(square_name)
        except ValueError:
            return None

        piece = self.board.piece_at(square)
        if piece is None:
            return None

        return {
            "type": PIECE_TYPE_MAP.get(piece.piece_type, "unknown"),
            "color": "white" if piece.color == chess.WHITE else "black",
            "square": square_name,
        }

    def get_all_pieces(self) -> list[dict[str, str]]:
        """Get all pieces currently on the board."""
        pieces = []
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                pieces.append({
                    "type": PIECE_TYPE_MAP.get(piece.piece_type, "unknown"),
                    "color": "white" if piece.color == chess.WHITE else "black",
                    "square": chess.square_name(square),
                })
        return pieces

    def get_material_balance(self) -> int:
        """Get material balance (positive = white advantage)."""
        balance = 0
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                value = PIECE_VALUES.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    balance += value
                else:
                    balance -= value
        return balance

    def get_board_summary(self) -> str:
        """Generate a human-readable board state summary for AI context."""
        pieces = self.get_all_pieces()
        white_pieces = [p for p in pieces if p["color"] == "white"]
        black_pieces = [p for p in pieces if p["color"] == "black"]
        balance = self.get_material_balance()

        summary = f"Turn: {self.turn}. "
        summary += f"Material: White={sum(PIECE_VALUES.get(getattr(chess, p['type'].upper(), 0), 0) for p in white_pieces)}, "
        summary += f"Black={sum(PIECE_VALUES.get(getattr(chess, p['type'].upper(), 0), 0) for p in black_pieces)}. "

        if balance > 0:
            summary += f"White is up +{balance} material. "
        elif balance < 0:
            summary += f"Black is up +{abs(balance)} material. "
        else:
            summary += "Material is equal. "

        if self.is_check:
            summary += f"{self.turn.capitalize()} is in CHECK! "

        return summary

    def _is_move_risky(self, move: chess.Move) -> bool:
        """Check if a piece would be attacked at its destination after the move."""
        # Temporarily make the move
        self.board.push(move)
        # Check if the destination square is attacked by opponent
        is_attacked = self.board.is_attacked_by(
            not self.board.turn,  # opponent of the side that just moved
            move.to_square,
        )
        self.board.pop()
        return is_attacked

    def get_game_result(self) -> str | None:
        """Get the game result if the game is over."""
        if not self.is_game_over:
            return None
        if self.is_checkmate:
            return "black_wins" if self.turn == "white" else "white_wins"
        if self.is_stalemate:
            return "stalemate"
        return "draw"

    def get_threats(self) -> list[str]:
        """Get a list of current threats (pieces under attack)."""
        threats = []
        opponent_color = chess.BLACK if self.board.turn == chess.WHITE else chess.WHITE

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                if self.board.is_attacked_by(opponent_color, square):
                    piece_name = PIECE_TYPE_MAP.get(piece.piece_type, "piece")
                    sq_name = chess.square_name(square)
                    threats.append(f"{piece_name.capitalize()} on {sq_name} is under attack")
        return threats
