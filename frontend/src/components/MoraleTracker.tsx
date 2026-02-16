/** Morale Tracker — displays morale bars for each piece */
import { BarChart3, TrendingUp, TrendingDown, Minus, Smile, Meh, Frown, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
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
    isCollapsed?: boolean;
    onToggle?: () => void;
}

export default function MoraleTracker({ pieces, playerColor, isCollapsed = true, onToggle }: MoraleTrackerProps) {
    const myPieces = pieces
        .filter((p) => p.color === playerColor && !p.is_captured)
        .sort((a, b) => {
            const order = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn'];
            return order.indexOf(a.piece_type) - order.indexOf(b.piece_type);
        });

    const avgMorale = myPieces.length
        ? Math.round(myPieces.reduce((sum, p) => sum + p.morale, 0) / myPieces.length)
        : 0;

    // Count pieces with low/critical morale (< 40)
    const criticalPieces = myPieces.filter(p => p.morale < 40).length;
    const lowMoralePieces = myPieces.filter(p => p.morale >= 40 && p.morale < 60).length;

    const TrendIcon = avgMorale >= 70 ? TrendingUp : avgMorale >= 40 ? Minus : TrendingDown;
    const ToggleIcon = isCollapsed ? ChevronDown : ChevronUp;

    return (
        <div className={`card morale-tracker ${isCollapsed ? 'morale-tracker-collapsed' : 'morale-tracker-expanded'}`}>
            <div
                className="card-header morale-tracker-header"
                onClick={onToggle}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        onToggle?.();
                    }
                }}
                aria-expanded={!isCollapsed}
                aria-controls="morale-tracker-content"
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                    <BarChart3 size={20} />
                    <span>Army Morale</span>
                </div>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-3)',
                }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'var(--space-1)',
                        fontSize: 'var(--text-sm)',
                        color: getMoraleColor(avgMorale),
                        fontWeight: 'var(--font-semibold)',
                    }}>
                        <TrendIcon size={16} />
                        {avgMorale}%
                    </div>
                    <ToggleIcon size={18} className="morale-toggle-icon" />
                </div>
            </div>

            {/* Collapsed state - show alert summary */}
            {isCollapsed && (
                <div className="morale-collapsed-summary">
                    {criticalPieces > 0 ? (
                        <div className="morale-alert morale-alert-critical">
                            <AlertCircle size={14} />
                            <span>{criticalPieces} piece{criticalPieces !== 1 ? 's' : ''} critical</span>
                        </div>
                    ) : lowMoralePieces > 0 ? (
                        <div className="morale-alert morale-alert-warning">
                            <AlertCircle size={14} />
                            <span>{lowMoralePieces} piece{lowMoralePieces !== 1 ? 's' : ''} low morale</span>
                        </div>
                    ) : (
                        <div className="morale-alert morale-alert-healthy">
                            <Smile size={14} />
                            <span>All pieces healthy</span>
                        </div>
                    )}
                </div>
            )}

            {/* Expanded state - show all pieces */}
            <div
                id="morale-tracker-content"
                className="morale-tracker-content"
                style={{
                    maxHeight: isCollapsed ? '0' : '500px',
                    opacity: isCollapsed ? 0 : 1,
                    overflow: 'hidden',
                    transition: 'max-height 0.3s ease, opacity 0.2s ease',
                }}
            >
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', paddingTop: 'var(--space-4)' }}>
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
        </div>
    );
}
