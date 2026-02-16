/** Join Page — auto-join a game via share code URL */
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { api } from '../lib/api';
import { useUIStore } from '../stores/uiStore';
import { ErrorState } from '../components/ui';

export default function JoinPage() {
    const { shareCode } = useParams<{ shareCode: string }>();
    const navigate = useNavigate();
    const showToast = useUIStore((state) => state.showToast);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!shareCode) {
            setError('No share code provided');
            return;
        }

        const joinGame = async () => {
            try {
                const game = await api.joinByShareCode(shareCode);
                showToast('Joined game successfully!', 'success');
                navigate(`/game/${game.id}`, { replace: true });
            } catch (err: unknown) {
                const msg = err instanceof Error ? err.message : 'Failed to join game';
                setError(msg);
                showToast(msg, 'error');
            }
        };

        joinGame();
    }, [shareCode, navigate, showToast]);

    if (error) {
        return (
            <ErrorState
                title="Failed to join game"
                message={error}
                retry={() => navigate('/lobby')}
            />
        );
    }

    return (
        <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '60vh',
            padding: 'var(--space-8)',
        }}>
            <div style={{ textAlign: 'center', maxWidth: '400px' }}>
                <Loader2 size={64} style={{
                    margin: '0 auto var(--space-4)',
                    animation: 'spin 1.5s linear infinite',
                    color: 'var(--primary-500)',
                }} />
                <h2 style={{
                    fontSize: 'var(--text-xl)',
                    fontWeight: 'var(--font-semibold)',
                    marginBottom: 'var(--space-2)',
                }}>
                    Joining game...
                </h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)' }}>
                    Please wait while we connect you to the game
                </p>
            </div>
        </div>
    );
}
