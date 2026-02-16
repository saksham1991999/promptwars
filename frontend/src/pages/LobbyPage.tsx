/** Lobby Page — create/join game, pick template (no login required) */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, Users, Crown, Zap, Flame, Rocket, Link, Copy, CheckCircle, Loader2, ArrowRight } from 'lucide-react';
import { api } from '../lib/api';
import { useUIStore } from '../stores/uiStore';
import { Button, Card, Input } from '../components/ui';
import type { TemplateName, GameMode, Game } from '../types/game';

const TEMPLATES: { id: TemplateName; name: string; IconComponent: typeof Crown; desc: string }[] = [
    { id: 'classic', name: 'Classic', IconComponent: Crown, desc: 'Standard chess with AI personalities' },
    { id: 'power_chess', name: 'Power Chess', IconComponent: Zap, desc: 'Chancellor + Archbishop variant' },
    { id: 'leaper_madness', name: 'Leaper Madness', IconComponent: Rocket, desc: 'Camels and Nightriders' },
    { id: 'hopper_havoc', name: 'Hopper Havoc', IconComponent: Flame, desc: 'Grasshoppers and Cannons' },
    { id: 'pawn_revolution', name: 'Pawn Revolution', IconComponent: Users, desc: 'Berolina Pawns take over' },
];

export default function LobbyPage() {
    const navigate = useNavigate();
    const showToast = useUIStore((state) => state.showToast);

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
                showToast('Game created! Starting...', 'success');
                navigate(`/game/${game.id}`);
            } else {
                setCreatedGame(game);
                showToast('Game created! Share the link with your friend.', 'success');
            }
        } catch (err: unknown) {
            const message = err instanceof Error ? err.message : 'Failed to create game';
            setError(message);
            showToast(message, 'error');
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
            showToast('Joined game successfully!', 'success');
            navigate(`/game/${game.id}`);
        } catch (err: unknown) {
            const message = err instanceof Error ? err.message : 'Failed to join game';
            setError(message);
            showToast(message, 'error');
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
        showToast('Link copied to clipboard!', 'success');
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="lobby-container">
            <h1 className="lobby-title">
                <span className="gradient-text">Game Lobby</span>
            </h1>

            {error && (
                <div className="auth-error" style={{
                    marginBottom: 'var(--space-4)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-2)',
                }}>
                    {error}
                </div>
            )}

            {!createdGame ? (
                <>
                    {/* Game Mode */}
                    <div style={{
                        display: 'flex',
                        gap: 'var(--space-3)',
                        marginBottom: 'var(--space-6)',
                        justifyContent: 'center',
                    }}>
                        <Button
                            variant={gameMode === 'pvai' ? 'primary' : 'secondary'}
                            onClick={() => setGameMode('pvai')}
                            icon={<Bot size={20} />}
                        >
                            Play vs AI
                        </Button>
                        <Button
                            variant={gameMode === 'pvp' ? 'primary' : 'secondary'}
                            onClick={() => setGameMode('pvp')}
                            icon={<Users size={20} />}
                        >
                            Play vs Friend
                        </Button>
                    </div>

                    {/* Template Selection */}
                    <h3 style={{
                        marginBottom: 'var(--space-4)',
                        textAlign: 'center',
                        color: 'var(--text-secondary)',
                        fontSize: 'var(--text-lg)',
                    }}>
                        Choose Your Battle
                    </h3>
                    <div className="template-grid">
                        {TEMPLATES.map((t) => {
                            const IconComponent = t.IconComponent;
                            return (
                                <div
                                    key={t.id}
                                    className={`template-card ${selectedTemplate === t.id ? 'selected' : ''}`}
                                    onClick={() => setSelectedTemplate(t.id)}
                                    role="button"
                                    tabIndex={0}
                                    aria-pressed={selectedTemplate === t.id}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' || e.key === ' ') {
                                            setSelectedTemplate(t.id);
                                        }
                                    }}
                                >
                                    <div className="template-icon" style={{
                                        width: '48px',
                                        height: '48px',
                                        borderRadius: '50%',
                                        background: selectedTemplate === t.id ? 'var(--primary-500)' : 'var(--surface-3)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        marginBottom: 'var(--space-2)',
                                        transition: 'all 0.2s ease',
                                    }}>
                                        <IconComponent size={24} color={selectedTemplate === t.id ? '#fff' : 'var(--primary-400)'} />
                                    </div>
                                    <div className="template-name">{t.name}</div>
                                    <p style={{
                                        fontSize: 'var(--text-xs)',
                                        color: 'var(--text-tertiary)',
                                        marginTop: 'var(--space-1)',
                                    }}>
                                        {t.desc}
                                    </p>
                                </div>
                            );
                        })}
                    </div>

                    <div style={{ textAlign: 'center', marginTop: 'var(--space-6)' }}>
                        <Button
                            variant="primary"
                            size="lg"
                            onClick={handleCreate}
                            disabled={loading}
                            loading={loading}
                            icon={loading ? undefined : <Zap size={20} />}
                        >
                            {loading ? 'Creating...' : 'Create Game'}
                        </Button>
                    </div>

                    {/* Join Section */}
                    <Card variant="glass" padding="lg" style={{ marginTop: 'var(--space-8)' }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 'var(--space-2)',
                            marginBottom: 'var(--space-4)',
                            fontSize: 'var(--text-lg)',
                            fontWeight: 'var(--font-semibold)',
                        }}>
                            <Link size={20} />
                            Join a Game
                        </div>
                        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
                            <Input
                                type="text"
                                value={joinCode}
                                onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                                placeholder="Enter share code..."
                                maxLength={12}
                                style={{ flex: 1 }}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') {
                                        handleJoin();
                                    }
                                }}
                            />
                            <Button
                                variant="primary"
                                onClick={handleJoin}
                                disabled={loading || !joinCode.trim()}
                                loading={loading}
                            >
                                Join
                            </Button>
                        </div>
                    </Card>
                </>
            ) : (
                /* Waiting for opponent */
                <Card variant="glass" padding="lg" style={{ textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
                    <CheckCircle size={64} color="var(--success-500)" style={{ margin: '0 auto var(--space-4)' }} />
                    <h2 style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--text-2xl)' }}>
                        Game Created!
                    </h2>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
                        Share this link with your opponent:
                    </p>

                    {/* Share URL */}
                    <div style={{
                        padding: 'var(--space-3)',
                        background: 'var(--surface-2)',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--surface-3)',
                        marginBottom: 'var(--space-3)',
                        wordBreak: 'break-all',
                    }}>
                        <code style={{ fontSize: 'var(--text-sm)', color: 'var(--primary-400)' }}>
                            {getInviteUrl()}
                        </code>
                    </div>

                    <Button
                        variant="primary"
                        onClick={handleCopyUrl}
                        icon={copied ? <CheckCircle size={16} /> : <Copy size={16} />}
                        style={{ marginBottom: 'var(--space-4)' }}
                    >
                        {copied ? 'Copied!' : 'Copy Invite Link'}
                    </Button>

                    <div style={{
                        padding: 'var(--space-3)',
                        background: 'rgba(99, 102, 241, 0.1)',
                        borderRadius: 'var(--radius-md)',
                        marginBottom: 'var(--space-4)',
                    }}>
                        <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                            Or share the code: <strong style={{ color: 'var(--text-primary)' }}>{createdGame.share_code}</strong>
                        </p>
                    </div>

                    <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: 'var(--space-3)',
                        marginTop: 'var(--space-6)',
                    }}>
                        <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-tertiary)' }}>
                            Waiting for opponent to join...
                        </p>
                        <Loader2 size={32} style={{ animation: 'spin 1.5s linear infinite', color: 'var(--primary-500)' }} />
                        <Button
                            variant="secondary"
                            onClick={() => navigate(`/game/${createdGame.id}`)}
                            icon={<ArrowRight size={16} />}
                        >
                            Go to Game
                        </Button>
                    </div>
                </Card>
            )}
        </div>
    );
}
