/** Error Boundary — catches React errors and displays fallback UI */
import { Component, type ReactNode } from 'react';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: string | null;
}

export default class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        };
    }

    static getDerivedStateFromError(error: Error): Partial<State> {
        // Update state so the next render shows the fallback UI
        return {
            hasError: true,
            error,
        };
    }

    componentDidCatch(error: Error, errorInfo: { componentStack: string }) {
        // Log error to console in development
        console.error('Error caught by boundary:', error, errorInfo);

        // Log to Sentry in production
        if (import.meta.env.PROD) {
            // Sentry will be initialized in main.tsx
            // @ts-ignore - Sentry is optional
            if (window.Sentry) {
                // @ts-ignore
                window.Sentry.captureException(error, {
                    contexts: {
                        react: {
                            componentStack: errorInfo.componentStack,
                        },
                    },
                });
            }
        }

        this.setState({
            errorInfo: errorInfo.componentStack,
        });
    }

    handleRetry = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
        });
        window.location.reload();
    };

    render() {
        if (this.state.hasError) {
            return (
                <div style={{
                    minHeight: '100vh',
                    background: 'var(--bg-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: 'var(--space-4)',
                }}>
                    <div style={{
                        background: 'var(--surface-2)',
                        border: '1px solid var(--danger-500)',
                        borderRadius: 'var(--radius-lg)',
                        boxShadow: 'var(--shadow-xl)',
                        maxWidth: '600px',
                        width: '100%',
                        padding: 'var(--space-8)',
                    }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 'var(--space-4)',
                            marginBottom: 'var(--space-6)',
                        }}>
                            <div style={{
                                width: '64px',
                                height: '64px',
                                background: 'rgba(239, 68, 68, 0.1)',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}>
                                <svg
                                    style={{ width: '32px', height: '32px', color: 'var(--danger-500)' }}
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                                    />
                                </svg>
                            </div>
                            <div>
                                <h1 style={{
                                    fontSize: 'var(--text-2xl)',
                                    fontWeight: 'var(--font-bold)',
                                    color: 'var(--text-primary)',
                                    margin: 0,
                                }}>Oops! Something went wrong</h1>
                                <p style={{
                                    fontSize: 'var(--text-base)',
                                    color: 'var(--text-secondary)',
                                    marginTop: 'var(--space-1)',
                                    margin: 0,
                                }}>
                                    An unexpected error occurred while rendering the page
                                </p>
                            </div>
                        </div>

                        {import.meta.env.DEV && this.state.error && (
                            <div style={{
                                background: 'var(--bg-secondary)',
                                borderRadius: 'var(--radius-md)',
                                padding: 'var(--space-4)',
                                marginBottom: 'var(--space-6)',
                                border: '1px solid var(--surface-3)',
                            }}>
                                <h2 style={{
                                    fontSize: 'var(--text-sm)',
                                    fontWeight: 'var(--font-semibold)',
                                    color: 'var(--danger-500)',
                                    marginBottom: 'var(--space-2)',
                                }}>Error Details:</h2>
                                <pre style={{
                                    fontSize: 'var(--text-xs)',
                                    color: 'var(--text-secondary)',
                                    overflowX: 'auto',
                                    whiteSpace: 'pre-wrap',
                                    wordBreak: 'break-word',
                                    fontFamily: 'var(--font-mono)',
                                    margin: 0,
                                }}>
                                    {this.state.error.toString()}
                                </pre>
                                {this.state.errorInfo && (
                                    <>
                                        <h3 style={{
                                            fontSize: 'var(--text-sm)',
                                            fontWeight: 'var(--font-semibold)',
                                            color: 'var(--danger-500)',
                                            marginTop: 'var(--space-4)',
                                            marginBottom: 'var(--space-2)',
                                        }}>
                                            Component Stack:
                                        </h3>
                                        <pre style={{
                                            fontSize: 'var(--text-xs)',
                                            color: 'var(--text-tertiary)',
                                            overflowX: 'auto',
                                            whiteSpace: 'pre-wrap',
                                            wordBreak: 'break-word',
                                            maxHeight: '160px',
                                            overflowY: 'auto',
                                            fontFamily: 'var(--font-mono)',
                                            margin: 0,
                                        }}>
                                            {this.state.errorInfo}
                                        </pre>
                                    </>
                                )}
                            </div>
                        )}

                        <div style={{ display: 'flex', gap: 'var(--space-4)' }}>
                            <button
                                onClick={this.handleRetry}
                                style={{
                                    flex: 1,
                                    background: 'linear-gradient(135deg, var(--primary-500), var(--primary-600))',
                                    color: '#ffffff',
                                    fontWeight: 'var(--font-semibold)',
                                    padding: 'var(--space-3) var(--space-6)',
                                    borderRadius: 'var(--radius-md)',
                                    border: 'none',
                                    cursor: 'pointer',
                                    transition: 'all var(--transition-normal)',
                                }}
                            >
                                Retry
                            </button>
                            <button
                                onClick={() => (window.location.href = '/')}
                                style={{
                                    flex: 1,
                                    background: 'var(--surface-3)',
                                    color: 'var(--text-primary)',
                                    fontWeight: 'var(--font-semibold)',
                                    padding: 'var(--space-3) var(--space-6)',
                                    borderRadius: 'var(--radius-md)',
                                    border: '1px solid rgba(255, 255, 255, 0.1)',
                                    cursor: 'pointer',
                                    transition: 'all var(--transition-normal)',
                                }}
                            >
                                Go Home
                            </button>
                        </div>

                        <p style={{
                            textAlign: 'center',
                            color: 'var(--text-muted)',
                            fontSize: 'var(--text-sm)',
                            marginTop: 'var(--space-6)',
                            margin: 'var(--space-6) 0 0 0',
                        }}>
                            If this problem persists, please contact support
                        </p>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
