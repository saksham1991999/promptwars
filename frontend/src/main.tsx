import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import ErrorBoundary from './components/ErrorBoundary';

// Initialize Sentry for error tracking (production only)
if (import.meta.env.PROD && import.meta.env.VITE_SENTRY_DSN) {
    import('@sentry/react').then((Sentry) => {
        Sentry.init({
            dsn: import.meta.env.VITE_SENTRY_DSN,
            environment: import.meta.env.MODE,
            tracesSampleRate: 0.1,
            replaysSessionSampleRate: 0.1,
            replaysOnErrorSampleRate: 1.0,
        });
        // Make Sentry available globally for ErrorBoundary
        // @ts-ignore
        window.Sentry = Sentry;
    });
}

// Initialize PostHog for product analytics
if (import.meta.env.VITE_POSTHOG_API_KEY) {
    import('posthog-js').then((posthog) => {
        posthog.default.init(import.meta.env.VITE_POSTHOG_API_KEY!, {
            api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://app.posthog.com',
            loaded: (ph) => {
                if (import.meta.env.DEV) {
                    ph.debug(); // Enable debug mode in development
                }
            },
        });
    });
}

// Initialize Google Analytics
if (import.meta.env.VITE_GA_MEASUREMENT_ID) {
    // gtag already loaded in index.html, just track initial page view
    if (typeof window.gtag !== 'undefined') {
        window.gtag('event', 'page_view', {
            page_title: document.title,
            page_location: window.location.href,
            page_path: window.location.pathname,
        });
    }
}

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ErrorBoundary>
            <App />
        </ErrorBoundary>
    </StrictMode>
);
