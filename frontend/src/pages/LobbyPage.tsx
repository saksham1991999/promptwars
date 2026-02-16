/** Lobby Page — create/join game, pick template (no login required) */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import type { TemplateName, GameMode, Game } from '../types/game';

const TEMPLATES: { id: TemplateName; name: string; icon: string; desc: string }[] = [
    { id: 'classic', name: 'Classic', icon: '♔', desc: 'Standard chess with AI personalities' },
    { id: 'power_chess', name: 'Power Chess', icon: '⚡', desc: 'Chancellor + Archbishop variant' },
    { id: 'leaper_madness', name: 'Leaper Madness', icon: '🦘', desc: 'Camels and Nightriders' },
    { id: 'hopper_havoc', name: 'Hopper Havoc', icon: '🦗', desc: 'Grasshoppers and Cannons' },
    { id: 'pawn_revolution', name: 'Pawn Revolution', icon: '✊', desc: 'Berolina Pawns take over' },
];

export default function LobbyPage() {
    const navigate = useNavigate();
    const [selectedTemplate, setSelectedTemplate] = useState<TemplateName>('classic');
    const [gameMode, setGameMode] = useState<GameMode>('pvai');
    const [createdGame, setCreatedGame] = useState<Game | null>(null);
    const [joinCode, setJoinCode] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [copied, setCopied] = useState(false);

    const handleCreate = async () => {
        setLoading(true);
        setError('');
        try {
            const game = await api.createGame({ game_mode: gameMode, template: selectedTemplate });
            if (gameMode === 'pvai') {
                navigate(`/game/${game.id}`);
            } else {
                setCreatedGame(game);
            }
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to create game');
        } finally {
            setLoading(false);
        }
    };

    const handleJoin = async () => {
        if (!joinCode.trim()) return;
        setLoading(true);
        setError('');
        try {
            const game = await api.joinByShareCode(joinCode.trim());
            navigate(`/game/${game.id}`);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to join game');
        } finally {
            setLoading(false);
        }
    };

    const getInviteUrl = () => {
        if (!createdGame) return '';
        return `${window.location.origin}/join/${createdGame.share_code}`;
    };

    const handleCopyUrl = () => {
        navigator.clipboard.writeText(getInviteUrl());
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="lobby-container">
            <h1 className="lobby-title">
                <span className="gradient-text">⚔️ Game Lobby</span>
            </h1>

            {error && <div className="auth-error" style={{ marginBottom: 'var(--space-4)' }}>{error}</div>}

            {!createdGame ? (
                <>
                    {/* Game Mode */}
                    <div style={{ display: 'flex', gap: 'var(--space-3)', marginBottom: 'var(--space-6)', justifyContent: 'center' }}>
                        <button
                            className={`btn ${gameMode === 'pvai' ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => setGameMode('pvai')}
                        >
                            🤖 Play vs AI
                        </button>
                        <button
                            className={`btn ${gameMode === 'pvp' ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => setGameMode('pvp')}
                        >
                            👥 Play vs Friend
                        </button>
                    </div>

                    {/* Template Selection */}
                    <h3 style={{ marginBottom: 'var(--space-4)', textAlign: 'center', color: 'var(--text-secondary)' }}>
                        Choose Your Battle
                    </h3>
                    <div className="template-grid">
                        {TEMPLATES.map((t) => (
                            <div
                                key={t.id}
                                className={`template-card ${selectedTemplate === t.id ? 'selected' : ''}`}
                                onClick={() => setSelectedTemplate(t.id)}
                            >
                                <div className="template-icon">{t.icon}</div>
                                <div className="template-name">{t.name}</div>
                                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', marginTop: 'var(--space-1)' }}>
                                    {t.desc}
                                </p>
                            </div>
                        ))}
                    </div>

                    <div style={{ textAlign: 'center', marginTop: 'var(--space-6)' }}>
                        <button className="btn btn-primary btn-lg" onClick={handleCreate} disabled={loading}>
                            {loading ? <><div className="spinner spinner-sm" /> Creating...</> : '🎮 Create Game'}
                        </button>
                    </div>

                    {/* Join Section */}
                    <div className="card" style={{ marginTop: 'var(--space-8)' }}>
                        <div className="card-header">🔗 Join a Game</div>
                        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
                            <input
                                className="input"
                                style={{ flex: 1 }}
                                type="text"
                                value={joinCode}
                                onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                                placeholder="Enter share code..."
                                maxLength={12}
                            />
                            <button className="btn btn-primary" onClick={handleJoin} disabled={loading || !joinCode.trim()}>
                                Join
                            </button>
                        </div>
                    </div>
                </>
            ) : (
                /* Waiting for opponent */
                <div style={{ textAlign: 'center' }}>
                    <div className="card">
                        <h2 style={{ marginBottom: 'var(--space-4)' }}>🎮 Game Created!</h2>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
                            Share this link with your opponent:
                        </p>

                        {/* Share URL */}
                        <div className="share-code-display" style={{ wordBreak: 'break-all' }}>
                            <code style={{ fontSize: 'var(--text-sm)', color: 'var(--accent-primary)' }}>
                                {getInviteUrl()}
                            </code>
                        </div>

                        <button
                            className="btn btn-primary"
                            style={{ marginTop: 'var(--space-3)' }}
                            onClick={handleCopyUrl}
                        >
                            {copied ? '✅ Copied!' : '📋 Copy Invite Link'}
                        </button>

                        <div style={{ marginTop: 'var(--space-4)', padding: 'var(--space-3)', background: 'rgba(108, 99, 255, 0.1)', borderRadius: 'var(--radius-md)' }}>
                            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                                Or share the code: <strong style={{ color: 'var(--text-primary)' }}>{createdGame.share_code}</strong>
                            </p>
                        </div>

                        <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', marginTop: 'var(--space-4)' }}>
                            Waiting for opponent to join...
                        </p>
                        <div className="spinner" style={{ margin: 'var(--space-4) auto' }} />

                        <button
                            className="btn btn-secondary"
                            style={{ marginTop: 'var(--space-2)' }}
                            onClick={() => navigate(`/game/${createdGame.id}`)}
                        >
                            Go to Game →
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
