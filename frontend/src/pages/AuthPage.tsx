/** Auth Page — login / signup */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function AuthPage() {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [username, setUsername] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login, signup } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (isLogin) {
                await login(email, password);
            } else {
                await signup(email, password, username || undefined);
            }
            navigate('/lobby');
        } catch (err: unknown) {
            const message = err instanceof Error ? err.message : 'An error occurred';
            setError(message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="card auth-card">
                <div className="card-header">
                    <span className="gradient-text">{isLogin ? '🔑 Welcome Back' : '🚀 Join PromptWars'}</span>
                </div>

                {error && <div className="auth-error">{error}</div>}

                <form className="auth-form" onSubmit={handleSubmit}>
                    {!isLogin && (
                        <div className="input-group">
                            <label className="input-label" htmlFor="username">Username</label>
                            <input
                                id="username"
                                className="input"
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="ChessKing42"
                                autoComplete="username"
                            />
                        </div>
                    )}

                    <div className="input-group">
                        <label className="input-label" htmlFor="email">Email</label>
                        <input
                            id="email"
                            className="input"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="player@example.com"
                            required
                            autoComplete="email"
                        />
                    </div>

                    <div className="input-group">
                        <label className="input-label" htmlFor="password">Password</label>
                        <input
                            id="password"
                            className="input"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                            minLength={6}
                            autoComplete={isLogin ? 'current-password' : 'new-password'}
                        />
                    </div>

                    <button className="btn btn-primary btn-lg" type="submit" disabled={loading} style={{ width: '100%' }}>
                        {loading ? (
                            <><div className="spinner spinner-sm" /> Loading...</>
                        ) : (
                            isLogin ? '🔑 Login' : '🚀 Create Account'
                        )}
                    </button>
                </form>

                <div className="auth-toggle">
                    {isLogin ? (
                        <>Don't have an account? <a href="#" onClick={(e) => { e.preventDefault(); setIsLogin(false); }}>Sign up</a></>
                    ) : (
                        <>Already have an account? <a href="#" onClick={(e) => { e.preventDefault(); setIsLogin(true); }}>Login</a></>
                    )}
                </div>
            </div>
        </div>
    );
}
