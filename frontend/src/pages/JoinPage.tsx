/** Join Page — auto-join a game via share code URL */
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';

export default function JoinPage() {
    const { shareCode } = useParams<{ shareCode: string }>();
    const navigate = useNavigate();
    const [error, setError] = useState('');

    useEffect(() => {
        if (!shareCode) return;

        const joinGame = async () => {
            try {
                const game = await api.joinByShareCode(shareCode);
                navigate(`/game/${game.id}`, { replace: true });
            } catch (err: unknown) {
                const msg = err instanceof Error ? err.message : 'Failed to join game';
                setError(msg);
            }
        };

        joinGame();
    }, [shareCode, navigate]);

    if (error) {
        return (
            <div style={{ textAlign: 'center', padding: 'var(--space-16)' }}>
                <h2 style={{ color: 'var(--text-error)', marginBottom: 'var(--space-4)' }}>
                    Failed to join game
                </h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
                    {error}
                </p>
                <button className="btn btn-primary" onClick={() => navigate('/lobby')}>
                    Go to Lobby
                </button>
            </div>
        );
    }

    return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
            <div style={{ textAlign: 'center' }}>
                <div className="spinner spinner-lg" style={{ margin: '0 auto var(--space-4)' }} />
                <p style={{ color: 'var(--text-secondary)' }}>
                    Joining game...
                </p>
            </div>
        </div>
    );
}
