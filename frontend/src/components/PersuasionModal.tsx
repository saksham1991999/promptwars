/** Persuasion Modal — lets the player argue with a refusing piece */
import { useState } from 'react';
import { X, Lightbulb, MessageSquare, TrendingUp, CheckCircle, XCircle } from 'lucide-react';
import { useUIStore } from '../stores/uiStore';
import { Button } from './ui';
import type { PersuasionResponse } from '../types/game';

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
    onSubmit: (argument: string) => Promise<void>;
    result: PersuasionResponse | null;
    isLoading: boolean;
}

export default function PersuasionModal({
    onSubmit,
    result,
    isLoading,
}: PersuasionModalProps) {
    const [argument, setArgument] = useState('');

    // Get piece and target from uiStore
    const persuasionModal = useUIStore((state) => state.persuasionModal);
    const closePersuasion = useUIStore((state) => state.closePersuasion);

    const { piece, target: targetSquare } = persuasionModal;

    if (!persuasionModal.isOpen || !piece || !targetSquare) {
        return null;
    }

    const handleSubmit = () => {
        if (argument.trim()) {
            onSubmit(argument.trim());
        }
    };

    const handleClose = () => {
        closePersuasion();
        setArgument('');
    };

    const charCount = argument.length;
    const maxChars = 500;
    const showWarning = charCount > maxChars * 0.8;

    return (
        <div
            className="modal-backdrop persuasion-modal"
            onClick={(e) => e.target === e.currentTarget && handleClose()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="persuasion-title"
        >
            <div className="modal">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
                    <div className="modal-title" id="persuasion-title" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                        <MessageSquare size={24} />
                        {PIECE_ICONS[piece.piece_type] || '?'} Persuade Your {piece.piece_type.charAt(0).toUpperCase() + piece.piece_type.slice(1)}
                    </div>
                    <button
                        onClick={handleClose}
                        style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'var(--text-tertiary)',
                            cursor: 'pointer',
                            padding: 'var(--space-2)',
                            borderRadius: 'var(--radius-sm)',
                            display: 'flex',
                            alignItems: 'center',
                        }}
                        aria-label="Close modal"
                    >
                        <X size={20} />
                    </button>
                </div>

                <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
                    Your {piece.piece_type} on <strong>{piece.square}</strong> refused to move to <strong>{targetSquare}</strong>.
                    Try convincing them!
                </p>

                {/* Piece info */}
                <div className="piece-info" style={{ marginBottom: 'var(--space-4)', display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
                    <span className="piece-info-icon" style={{ fontSize: '2rem' }}>{PIECE_ICONS[piece.piece_type]}</span>
                    <div className="piece-info-details">
                        <div style={{ fontSize: 'var(--text-base)', fontWeight: 'var(--font-semibold)', marginBottom: 'var(--space-1)' }}>
                            {piece.personality.archetype}
                        </div>
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                            Morale: <span style={{ color: piece.morale >= 60 ? 'var(--success-500)' : 'var(--warning-500)' }}>{piece.morale}%</span>
                            {' • '}
                            {piece.personality.traits.slice(0, 2).join(', ')}
                        </div>
                    </div>
                </div>

                {/* Tip */}
                <div style={{
                    display: 'flex',
                    gap: 'var(--space-2)',
                    padding: 'var(--space-3)',
                    background: 'rgba(99, 102, 241, 0.1)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: 'var(--text-sm)',
                    color: 'var(--primary-400)',
                    marginBottom: 'var(--space-4)',
                    border: '1px solid rgba(99, 102, 241, 0.2)',
                }}>
                    <Lightbulb size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>{PERSUASION_TIPS[piece.piece_type] || 'Try to appeal to this piece\'s personality!'}</span>
                </div>

                {!result ? (
                    <>
                        <div style={{ marginBottom: 'var(--space-2)' }}>
                            <textarea
                                className="persuasion-textarea"
                                value={argument}
                                onChange={(e) => setArgument(e.target.value.slice(0, maxChars))}
                                placeholder="Why should this piece follow your order? Be specific and persuasive..."
                                disabled={isLoading}
                                maxLength={maxChars}
                                rows={5}
                                aria-label="Persuasion argument"
                            />
                            <div style={{
                                fontSize: 'var(--text-xs)',
                                color: showWarning ? 'var(--warning-500)' : 'var(--text-tertiary)',
                                marginTop: 'var(--space-1)',
                                textAlign: 'right',
                            }}>
                                {charCount}/{maxChars} characters
                            </div>
                        </div>

                        <div className="modal-actions" style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-4)' }}>
                            <Button variant="ghost" onClick={handleClose} disabled={isLoading} style={{ flex: 1 }}>
                                Cancel
                            </Button>
                            <Button
                                variant="primary"
                                onClick={handleSubmit}
                                disabled={isLoading || !argument.trim()}
                                loading={isLoading}
                                icon={isLoading ? undefined : <MessageSquare size={16} />}
                                style={{ flex: 1 }}
                            >
                                {isLoading ? 'Persuading...' : 'Persuade'}
                            </Button>
                        </div>
                    </>
                ) : (
                    <>
                        {/* Result */}
                        <div style={{
                            display: 'flex',
                            gap: 'var(--space-3)',
                            padding: 'var(--space-4)',
                            background: result.success ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                            border: `1px solid ${result.success ? 'var(--success-500)' : 'var(--danger-500)'}`,
                            borderRadius: 'var(--radius-md)',
                            marginBottom: 'var(--space-4)',
                        }}>
                            <div style={{ flexShrink: 0 }}>
                                {result.success ? <CheckCircle size={24} color="var(--success-500)" /> : <XCircle size={24} color="var(--danger-500)" />}
                            </div>
                            <div>
                                <p style={{ fontWeight: 'var(--font-bold)', marginBottom: 'var(--space-2)', fontSize: 'var(--text-lg)' }}>
                                    {result.success ? 'Persuasion Successful!' : 'Persuasion Failed'}
                                </p>
                                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
                                    "{result.piece_response}"
                                </p>
                            </div>
                        </div>

                        {/* Stats */}
                        <div className="persuasion-stats" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
                            <div className="persuasion-stat" style={{ textAlign: 'center' }}>
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-1)', marginBottom: 'var(--space-1)' }}>
                                    <TrendingUp size={16} color="var(--primary-500)" />
                                    <div className="persuasion-stat-value" style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--font-bold)' }}>
                                        {Math.round(result.probability * 100)}%
                                    </div>
                                </div>
                                <div className="persuasion-stat-label" style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>Success Rate</div>
                            </div>
                            <div className="persuasion-stat" style={{ textAlign: 'center' }}>
                                <div className="persuasion-stat-value" style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--font-bold)', marginBottom: 'var(--space-1)' }}>
                                    {result.evaluation.logic_score}/25
                                </div>
                                <div className="persuasion-stat-label" style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>Logic Score</div>
                            </div>
                            <div className="persuasion-stat" style={{ textAlign: 'center' }}>
                                <div className="persuasion-stat-value" style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--font-bold)', marginBottom: 'var(--space-1)' }}>
                                    {result.evaluation.personality_match}/15
                                </div>
                                <div className="persuasion-stat-label" style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>Personality</div>
                            </div>
                        </div>

                        <div className="modal-actions">
                            <Button variant="primary" onClick={handleClose} style={{ width: '100%' }}>
                                {result.move_executed ? 'Continue' : 'Close'}
                            </Button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
