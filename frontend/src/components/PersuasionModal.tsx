/** Persuasion Modal — lets the player argue with a refusing piece */
import { useState } from 'react';
import type { GamePiece, PersuasionResponse } from '../types/game';

const PIECE_ICONS: Record<string, string> = {
    king: '♚', queen: '♛', rook: '♜', bishop: '♝', knight: '♞', pawn: '♟',
};

const PERSUASION_TIPS: Record<string, string> = {
    pawn: 'Pawns respond to teamwork, duty, and promotion dreams.',
    knight: 'Knights love glory, bravery, and adventure.',
    bishop: 'Bishops appreciate logic, tactics, and calculated reasoning.',
    rook: 'Rooks value duty, discipline, and strategic orders.',
    queen: 'The Queen needs to feel protected and valued.',
    king: 'The King needs assurance of safety above all.',
};

interface PersuasionModalProps {
    piece: GamePiece;
    targetSquare: string;
    onSubmit: (argument: string) => Promise<void>;
    onClose: () => void;
    result: PersuasionResponse | null;
    isLoading: boolean;
}

export default function PersuasionModal({
    piece,
    targetSquare,
    onSubmit,
    onClose,
    result,
    isLoading,
}: PersuasionModalProps) {
    const [argument, setArgument] = useState('');

    const handleSubmit = () => {
        if (argument.trim()) {
            onSubmit(argument.trim());
        }
    };

    return (
        <div className="modal-backdrop persuasion-modal" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="modal">
                <div className="modal-title">
                    {PIECE_ICONS[piece.piece_type] || '?'} Persuade Your {piece.piece_type.charAt(0).toUpperCase() + piece.piece_type.slice(1)}
                </div>

                <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
                    Your {piece.piece_type} on <strong>{piece.square}</strong> refused to move to <strong>{targetSquare}</strong>.
                    Try convincing them!
                </p>

                {/* Piece info */}
                <div className="piece-info" style={{ marginBottom: 'var(--space-4)' }}>
                    <span className="piece-info-icon">{PIECE_ICONS[piece.piece_type]}</span>
                    <div className="piece-info-details">
                        <span className="piece-info-name">{piece.personality.archetype}</span>
                        <span className="piece-info-personality">
                            Morale: {piece.morale}% • Traits: {piece.personality.traits.join(', ')}
                        </span>
                    </div>
                </div>

                {/* Tip */}
                <div style={{
                    padding: 'var(--space-3)',
                    background: 'rgba(108, 99, 255, 0.08)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: 'var(--text-xs)',
                    color: 'var(--text-accent)',
                    marginBottom: 'var(--space-4)',
                }}>
                    💡 {PERSUASION_TIPS[piece.piece_type] || 'Try to appeal to this piece\'s personality!'}
                </div>

                {!result ? (
                    <>
                        <textarea
                            className="persuasion-textarea"
                            value={argument}
                            onChange={(e) => setArgument(e.target.value)}
                            placeholder="Why should this piece follow your order? Be specific and persuasive..."
                            disabled={isLoading}
                            maxLength={500}
                        />
                        <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', marginTop: 'var(--space-1)' }}>
                            {argument.length}/500 characters
                        </p>

                        <div className="modal-actions">
                            <button className="btn btn-ghost" onClick={onClose} disabled={isLoading}>Cancel</button>
                            <button
                                className="btn btn-primary"
                                onClick={handleSubmit}
                                disabled={isLoading || !argument.trim()}
                            >
                                {isLoading ? (
                                    <><div className="spinner spinner-sm" /> Persuading...</>
                                ) : (
                                    '🗣️ Persuade'
                                )}
                            </button>
                        </div>
                    </>
                ) : (
                    <>
                        {/* Result */}
                        <div style={{
                            padding: 'var(--space-4)',
                            background: result.success ? 'rgba(0, 230, 118, 0.08)' : 'rgba(239, 83, 80, 0.08)',
                            border: `1px solid ${result.success ? 'rgba(0, 230, 118, 0.2)' : 'rgba(239, 83, 80, 0.2)'}`,
                            borderRadius: 'var(--radius-md)',
                            marginBottom: 'var(--space-4)',
                        }}>
                            <p style={{ fontWeight: 'var(--font-bold)', marginBottom: 'var(--space-2)' }}>
                                {result.success ? '✅ Persuasion Successful!' : '❌ Persuasion Failed'}
                            </p>
                            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
                                "{result.piece_response}"
                            </p>
                        </div>

                        {/* Stats */}
                        <div className="persuasion-stats">
                            <div className="persuasion-stat">
                                <div className="persuasion-stat-value">{Math.round(result.probability * 100)}%</div>
                                <div className="persuasion-stat-label">Success Rate</div>
                            </div>
                            <div className="persuasion-stat">
                                <div className="persuasion-stat-value">{result.evaluation.logic_score}/25</div>
                                <div className="persuasion-stat-label">Logic Score</div>
                            </div>
                            <div className="persuasion-stat">
                                <div className="persuasion-stat-value">{result.evaluation.personality_match}/15</div>
                                <div className="persuasion-stat-label">Personality</div>
                            </div>
                        </div>

                        <div className="modal-actions">
                            <button className="btn btn-primary" onClick={onClose}>
                                {result.move_executed ? 'Continue' : 'Close'}
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
