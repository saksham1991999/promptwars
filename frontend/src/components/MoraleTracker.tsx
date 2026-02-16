/** Morale Tracker — displays morale bars for each piece */
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

function getMoraleLabel(morale: number): string {
    if (morale >= 80) return '😄 Enthusiastic';
    if (morale >= 60) return '🙂 Normal';
    if (morale >= 40) return '😐 Reluctant';
    if (morale >= 20) return '😟 Demoralized';
    return '😤 Mutinous';
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

    return (
        <div className="card">
            <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>📊 Army Morale</span>
                <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
                    Avg: {avgMorale}%
                </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {myPieces.map((piece) => (
                    <div key={piece.id} className={`morale-bar-container ${getMoraleClass(piece.morale)}`}>
                        <div className="morale-bar-label">
                            <span>
                                {PIECE_ICONS[piece.piece_type] || '?'} {piece.piece_type.charAt(0).toUpperCase() + piece.piece_type.slice(1)}
                                {piece.square && <span style={{ color: 'var(--text-tertiary)', marginLeft: '4px' }}>({piece.square})</span>}
                            </span>
                            <span>{piece.morale}% — {getMoraleLabel(piece.morale).split(' ')[0]}</span>
                        </div>
                        <div className="morale-bar">
                            <div className="morale-bar-fill" style={{ width: `${piece.morale}%` }} />
                        </div>
                    </div>
                ))}
            </div>

            {myPieces.length === 0 && (
                <p style={{ color: 'var(--text-tertiary)', textAlign: 'center', padding: 'var(--space-4)' }}>
                    No active pieces
                </p>
            )}
        </div>
    );
}
