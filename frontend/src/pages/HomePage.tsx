/** Home Page — landing page with hero section (no auth required) */
import { useNavigate } from 'react-router-dom';

const FEATURES = [
    { icon: '🤖', title: 'AI Personalities', description: 'Each piece has a unique personality, morale, and opinions. They might refuse your orders!' },
    { icon: '🗣️', title: 'Persuasion System', description: 'When pieces refuse, talk them into it. Use logic, flattery, or appeal to their personality.' },
    { icon: '👑', title: 'King Taunts', description: 'The opponent\'s King will trash-talk you. Can you keep your composure under pressure?' },
    { icon: '📊', title: 'AI Analysis', description: 'Get real-time AI move analysis and commentary. Learn from every move you make.' },
    { icon: '⚡', title: 'Morale System', description: 'Victories boost morale, blunders destroy it. Manage your army\'s psychology to win.' },
    { icon: '🎨', title: 'Custom Pieces', description: 'Create themed armies with AI. Pirates, robots, dragons — your imagination is the limit.' },
];

export default function HomePage() {
    const navigate = useNavigate();

    return (
        <div className="home-hero">
            <h1 className="home-title">
                <span className="gradient-text">PromptWars</span>
                <br />
                Chess Where Pieces Fight Back
            </h1>

            <p className="home-subtitle">
                Command your army in a chess game where pieces have AI personalities,
                morale, and opinions. Persuade reluctant pieces, survive King taunts,
                and outsmart your opponent's psychology.
            </p>

            <div className="home-actions">
                <button className="btn btn-primary btn-lg" onClick={() => navigate('/lobby')}>
                    ⚔️ Play Now
                </button>
            </div>

            <div className="home-features">
                {FEATURES.map((f) => (
                    <div className="feature-card" key={f.title}>
                        <div className="feature-icon">{f.icon}</div>
                        <div className="feature-title">{f.title}</div>
                        <div className="feature-description">{f.description}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
