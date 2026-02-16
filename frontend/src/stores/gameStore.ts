import { create } from 'zustand';
import { Chess, type Square } from 'chess.js';
import type { Game, GamePiece } from '../types/game';

interface GameStore {
  // State
  game: Game | null;
  pieces: GamePiece[];
  chess: Chess;
  selectedSquare: string | null;
  legalMoves: string[];
  isLoading: boolean;
  error: string | null;

  // Actions
  setGame: (game: Game) => void;
  setPieces: (pieces: GamePiece[]) => void;
  setChess: (chess: Chess) => void;
  selectSquare: (square: string | null) => void;
  setLegalMoves: (moves: string[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  updatePieceMorale: (pieceId: string, morale: number) => void;
  reset: () => void;
}

const initialState = {
  game: null,
  pieces: [],
  chess: new Chess(),
  selectedSquare: null,
  legalMoves: [],
  isLoading: false,
  error: null,
};

export const useGameStore = create<GameStore>((set, get) => ({
  ...initialState,

  setGame: (game) => set({ game, error: null }),

  setPieces: (pieces) => set({ pieces }),

  setChess: (chess) => set({ chess }),

  selectSquare: (square) => {
    const { chess, selectedSquare } = get();

    // If clicking the same square, deselect
    if (square === selectedSquare) {
      set({ selectedSquare: null, legalMoves: [] });
      return;
    }

    // If no square selected yet, select this one and calculate legal moves
    if (!selectedSquare && square) {
      try {
        const moves = chess.moves({ square: square as Square, verbose: true });
        const legalSquares = moves.map((move) => move.to);
        set({ selectedSquare: square, legalMoves: legalSquares });
      } catch {
        // Invalid square, ignore
        set({ selectedSquare: null, legalMoves: [] });
      }
      return;
    }

    // If a different square is selected, deselect
    set({ selectedSquare: square, legalMoves: [] });
  },

  setLegalMoves: (moves) => set({ legalMoves: moves }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error, isLoading: false }),

  updatePieceMorale: (pieceId, morale) => {
    const { pieces } = get();
    const updatedPieces = pieces.map((piece) =>
      piece.id === pieceId ? { ...piece, morale } : piece
    );
    set({ pieces: updatedPieces });
  },

  reset: () => set(initialState),
}));
