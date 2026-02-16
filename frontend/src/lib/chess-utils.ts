/**
 * Chess utilities - shared constants and helper functions
 */

import type { GamePiece } from '../types/game';

/** Unicode chess piece icons by type */
export const PIECE_ICONS: Record<string, string> = {
  king: '♔',
  queen: '♕',
  rook: '♖',
  bishop: '♗',
  knight: '♘',
  pawn: '♙',
};

/** Piece type ordering for consistent display */
export const PIECE_ORDER = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn'];

/**
 * Sort pieces by type order (king first, pawn last)
 */
export function sortPieces(pieces: GamePiece[]): GamePiece[] {
  return pieces.sort((a, b) => {
    const aIndex = PIECE_ORDER.indexOf(a.piece_type);
    const bIndex = PIECE_ORDER.indexOf(b.piece_type);
    return aIndex - bIndex;
  });
}

/**
 * Get piece icon by type
 */
export function getPieceIcon(pieceType: string): string {
  return PIECE_ICONS[pieceType] || '?';
}

/**
 * Convert square notation to board coordinates
 */
export function squareToCoords(square: string): { file: number; rank: number } {
  const file = square.charCodeAt(0) - 'a'.charCodeAt(0);
  const rank = parseInt(square[1], 10) - 1;
  return { file, rank };
}

/**
 * Convert board coordinates to square notation
 */
export function coordsToSquare(file: number, rank: number): string {
  return String.fromCharCode('a'.charCodeAt(0) + file) + (rank + 1);
}
