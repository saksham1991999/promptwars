/** Home Page — landing page with hero section (no auth required) */
import { useNavigate } from 'react-router-dom';
import { Bot, MessageSquare, Crown, BarChart3, Zap, Palette, Swords, ArrowRight, Cloud, Cpu, Shield, Globe } from 'lucide-react';
import { Button } from '../components/ui';

const GOOGLE_CLOUD_FEATURES = [
    { icon: Cpu, title: 'Google Gemini AI', description: 'All piece personalities powered by Google Gemini 3 Flash for natural, contextual dialogue and analysis.' },
    { icon: Cloud, title: 'Google Cloud Run', description: 'Serverless infrastructure that scales automatically from 0 to thousands of concurrent games.' },
    { icon: Shield, title: 'Enterprise Security', description: 'Google Secret Manager protects all API keys and credentials with enterprise-grade encryption.' },
    { icon: Globe, title: 'Global Edge Network', description: "Deployed on Google's global infrastructure for low-latency gameplay worldwide." },
];

const FEATURES = [
    { icon: Bot, title: 'AI Personalities', description: 'Each piece has a unique personality, morale, and opinions. They might refuse your orders!' },
    { icon: MessageSquare, title: 'Persuasion System', description: 'When pieces refuse, talk them into it. Use logic, flattery, or appeal to their personality.' },
    { icon: Crown, title: 'King Taunts', description: 'The opponent\'s King will trash-talk you. Can you keep your composure under pressure?' },
    { icon: BarChart3, title: 'AI Analysis', description: 'Get real-time AI move analysis and commentary. Learn from every move you make.' },
    { icon: Zap, title: 'Morale System', description: 'Victories boost morale, blunders destroy it. Manage your army\'s psychology to win.' },
    { icon: Palette, title: 'Custom Pieces', description: 'Create themed armies with AI. Pirates, robots, dragons — your imagination is the limit.' },
];

export default function HomePage() {
    const navigate = useNavigate();

    return (
        <div className="home-hero">
            <h1 className="home-title">
                <span className="gradient-text">Chess Alive</span>
                <br />
                Chess Where Pieces Fight Back
            </h1>

            <p className="home-subtitle">
                Command your army in a chess game where pieces have AI personalities,
                morale, and opinions. Persuade reluctant pieces, survive King taunts,
                and outsmart your opponent's psychology.
            </p>

            <div className="home-actions">
                <Button
                    variant="primary"
                    size="lg"
                    onClick={() => navigate('/lobby')}
                    icon={<Swords size={20} />}
                >
                    Play Now
                </Button>
            </div>

            <div className="home-features">
                {FEATURES.map((f) => {
                    const IconComponent = f.icon;
                    return (
                        <div className="feature-card" key={f.title}>
                            <div className="feature-icon" style={{
                                width: '48px',
                                height: '48px',
                                borderRadius: '50%',
                                background: 'var(--surface-3)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                marginBottom: 'var(--space-3)',
                            }}>
                                <IconComponent size={24} color="var(--primary-400)" />
                            </div>
                            <div className="feature-title">{f.title}</div>
                            <div className="feature-description">{f.description}</div>
                        </div>
                    );
                })}
            </div>

            {/* Google Cloud Section */}
            <div style={{
                marginTop: 'var(--space-16)',
                paddingTop: 'var(--space-12)',
                borderTop: '1px solid var(--surface-2)',
                textAlign: 'center',
            }}>
                <p style={{
                    color: 'var(--text-secondary)',
                    fontSize: 'var(--text-sm)',
                    marginBottom: 'var(--space-3)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                }}>
                    Powered by
                </p>
                <h2 style={{
                    fontSize: 'var(--text-3xl)',
                    fontWeight: 'var(--font-bold)',
                    marginBottom: 'var(--space-10)',
                }}>
                    <span style={{ color: '#4285F4' }}>G</span>
                    <span style={{ color: '#EA4335' }}>o</span>
                    <span style={{ color: '#FBBC05' }}>o</span>
                    <span style={{ color: '#4285F4' }}>g</span>
                    <span style={{ color: '#34A853' }}>l</span>
                    <span style={{ color: '#EA4335' }}>e</span>
                    {' '}Cloud
                </h2>
                <div className="home-features">
                    {GOOGLE_CLOUD_FEATURES.map((f) => {
                        const IconComponent = f.icon;
                        return (
                            <div className="feature-card" key={f.title}>
                                <div className="feature-icon" style={{
                                    width: '48px',
                                    height: '48px',
                                    borderRadius: '50%',
                                    background: 'var(--surface-3)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    marginBottom: 'var(--space-3)',
                                }}>
                                    <IconComponent size={24} color="#4285F4" />
                                </div>
                                <div className="feature-title">{f.title}</div>
                                <div className="feature-description">{f.description}</div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Quick links */}
            <div style={{
                marginTop: 'var(--space-12)',
                textAlign: 'center',
                color: 'var(--text-tertiary)',
                fontSize: 'var(--text-sm)',
            }}>
                <p style={{ marginBottom: 'var(--space-2)' }}>
                    Ready to command your army?
                </p>
                <button
                    onClick={() => navigate('/lobby')}
                    style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--primary-400)',
                        cursor: 'pointer',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 'var(--space-1)',
                        fontSize: 'var(--text-sm)',
                        fontWeight: 'var(--font-semibold)',
                    }}
                >
                    Start Playing
                    <ArrowRight size={16} />
                </button>
            </div>
        </div>
    );
}
