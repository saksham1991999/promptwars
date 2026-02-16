/** Morale Tracker — displays morale bars for each piece */
import { BarChart3, TrendingUp, TrendingDown, Minus, Smile, Meh, Frown } from 'lucide-react';
import type { GamePiece } from '../types/game';

const PIECE_ICONS: Record<string, string> = {
    king: '♚', queen: '♛', rook: '♜', bishop: '♝', knight: '♞', pawn: '♟',
};

function getMoraleClass(morale: number): string {
    if (morale >= 80) return 'morale-high';
    if (morale >= 60) return 'morale-normal';
    if (morale >= 40) return 'morale-medium';
    if (morale >= 20) return 'morale-low';
    return 'morale-critical';
}

function getMoraleColor(morale: number): string {
    if (morale >= 80) return 'var(--morale-high)';
    if (morale >= 60) return 'var(--morale-normal)';
    if (morale >= 40) return 'var(--morale-medium)';
    if (morale >= 20) return 'var(--morale-low)';
    return 'var(--morale-critical)';
}

function getMoraleIcon(morale: number) {
    if (morale >= 80) return <Smile size={14} />;
    if (morale >= 40) return <Meh size={14} />;
    return <Frown size={14} />;
}


interface MoraleTrackerProps {
    pieces: GamePiece[];
    playerColor: 'white' | 'black';
}

export default function MoraleTracker({ pieces, playerColor }: MoraleTrackerProps) {
    const myPieces = pieces
        .filter((p) => p.color === playerColor && !p.is_captured)
        .sort((a, b) => {
            const order = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn'];
            return order.indexOf(a.piece_type) - order.indexOf(b.piece_type);
        });

    const avgMorale = myPieces.length
        ? Math.round(myPieces.reduce((sum, p) => sum + p.morale, 0) / myPieces.length)
        : 0;

    const TrendIcon = avgMorale >= 70 ? TrendingUp : avgMorale >= 40 ? Minus : TrendingDown;

    return (
        <div className="card">
            <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                    <BarChart3 size={20} />
                    <span>Army Morale</span>
                </div>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-2)',
                    fontSize: 'var(--text-sm)',
                    color: getMoraleColor(avgMorale),
                    fontWeight: 'var(--font-semibold)',
                }}>
                    <TrendIcon size={16} />
                    {avgMorale}%
                </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {myPieces.map((piece) => (
                    <div
                        key={piece.id}
                        className={`morale-bar-container ${getMoraleClass(piece.morale)}`}
                        role="progressbar"
                        aria-valuenow={piece.morale}
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-label={`${piece.piece_type} morale: ${piece.morale}%`}
                    >
                        <div className="morale-bar-label">
                            <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                                {PIECE_ICONS[piece.piece_type] || '?'} {piece.piece_type.charAt(0).toUpperCase() + piece.piece_type.slice(1)}
                                {piece.square && <span style={{ color: 'var(--text-tertiary)', fontSize: 'var(--text-xs)' }}>({piece.square})</span>}
                            </span>
                            <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)', fontSize: 'var(--text-xs)' }}>
                                {getMoraleIcon(piece.morale)}
                                {piece.morale}%
                            </span>
                        </div>
                        <div className="morale-bar">
                            <div
                                className="morale-bar-fill"
                                style={{
                                    width: `${piece.morale}%`,
                                    background: `linear-gradient(90deg, ${getMoraleColor(piece.morale)}, ${getMoraleColor(piece.morale)}dd)`,
                                    transition: 'width 0.3s ease, background 0.3s ease',
                                }}
                            />
                        </div>
                    </div>
                ))}
            </div>

            {myPieces.length === 0 && (
                <p style={{
                    color: 'var(--text-tertiary)',
                    textAlign: 'center',
                    padding: 'var(--space-4)',
                    fontSize: 'var(--text-sm)',
                }}>
                    No active pieces
                </p>
            )}
        </div>
    );
}
