/** Chess Board component — renders an interactive 8×8 board with pieces */
import { useMemo } from 'react';
import type { GamePiece, PieceColor } from '../types/game';

// Unicode chess piece symbols
const PIECE_SYMBOLS: Record<string, Record<PieceColor, string>> = {
    king: { white: '♔', black: '♚' },
    queen: { white: '♕', black: '♛' },
    rook: { white: '♖', black: '♜' },
    bishop: { white: '♗', black: '♝' },
    knight: { white: '♘', black: '♞' },
    pawn: { white: '♙', black: '♟' },
};

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
const RANKS = ['8', '7', '6', '5', '4', '3', '2', '1'];

interface ChessBoardProps {
    pieces: GamePiece[];
    playerColor: PieceColor;
    lastMove?: { from_square: string; to_square: string } | null;
    checkSquare?: string | null;
    legalMoves?: string[];
    selectedSquare: string | null;
    onSquareClick: (square: string) => void;
}

export default function ChessBoard({
    pieces,
    playerColor,
    lastMove,
    checkSquare,
    legalMoves = [],
    selectedSquare,
    onSquareClick,
}: ChessBoardProps) {
    // Build piece lookup map
    const pieceMap = useMemo(() => {
        const map = new Map<string, GamePiece>();
        for (const piece of pieces) {
            if (piece.square && !piece.is_captured) {
                map.set(piece.square, piece);
            }
        }
        return map;
    }, [pieces]);

    // Determine ranks/files order based on player color
    const ranksDisplay = playerColor === 'white' ? RANKS : [...RANKS].reverse();
    const filesDisplay = playerColor === 'white' ? FILES : [...FILES].reverse();

    return (
        <div className="chess-board-container">
            <div className="chess-board" role="grid" aria-label="Chess board">
                {ranksDisplay.map((rank, rankIdx) =>
                    filesDisplay.map((file, fileIdx) => {
                        const square = `${file}${rank}`;
                        const isLight = (rankIdx + fileIdx) % 2 === 0;
                        const piece = pieceMap.get(square);
                        const isSelected = selectedSquare === square;
                        const isMoveHint = legalMoves.includes(square) && !pieceMap.has(square);
                        const isCaptureHint = legalMoves.includes(square) && pieceMap.has(square);
                        const isLastMove = lastMove && (lastMove.from_square === square || lastMove.to_square === square);
                        const isCheck = checkSquare === square;

                        const classes = [
                            'chess-square',
                            isLight ? 'light' : 'dark',
                            isSelected && 'selected',
                            isMoveHint && 'move-hint',
                            isCaptureHint && 'capture-hint',
                            isLastMove && 'last-move',
                            isCheck && 'check',
                        ].filter(Boolean).join(' ');

                        return (
                            <div
                                key={square}
                                className={classes}
                                onClick={() => onSquareClick(square)}
                                role="gridcell"
                                aria-label={`${square}${piece ? ` ${piece.color} ${piece.piece_type}` : ''}`}
                                data-square={square}
                            >
                                {/* Rank label */}
                                {fileIdx === 0 && (
                                    <span className="chess-rank-label" style={{ color: isLight ? '#b58863' : '#f0d9b5' }}>
                                        {rank}
                                    </span>
                                )}
                                {/* File label */}
                                {rankIdx === ranksDisplay.length - 1 && (
                                    <span className="chess-file-label" style={{ color: isLight ? '#b58863' : '#f0d9b5' }}>
                                        {file}
                                    </span>
                                )}
                                {/* Piece */}
                                {piece && (
                                    <span className="chess-piece" role="img" aria-label={`${piece.color} ${piece.piece_type}`}>
                                        {PIECE_SYMBOLS[piece.piece_type]?.[piece.color] || '?'}
                                    </span>
                                )}
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
}
