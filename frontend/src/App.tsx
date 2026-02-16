/** Main App — routing, layout (no auth required) */
import { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import { Crown, Swords } from 'lucide-react';
import ErrorBoundary from './components/ErrorBoundary';
import { useUIStore } from './stores/uiStore';
import { ToastContainer, Button, Skeleton } from './components/ui';
import './App.css';

// Route-based code splitting
const HomePage = lazy(() => import('./pages/HomePage'));
const LobbyPage = lazy(() => import('./pages/LobbyPage'));
const GamePage = lazy(() => import('./pages/GamePage'));
const JoinPage = lazy(() => import('./pages/JoinPage'));

function Header() {
  return (
    <header className="header">
      <Link
        to="/"
        className="header-logo"
        style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
      >
        <Crown size={24} />
        <span className="gradient-text">Chess Alive</span>
      </Link>
      <nav className="header-nav">
        <Link to="/lobby">
          <Button variant="primary" size="sm" icon={<Swords size={16} />}>
            Play Now
          </Button>
        </Link>
      </nav>
    </header>
  );
}

function LoadingFallback() {
  return (
    <div style={{
      minHeight: '60vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 'var(--space-8)',
    }}>
      <div style={{ maxWidth: '800px', width: '100%' }}>
        <Skeleton variant="rectangular" height="400px" />
      </div>
    </div>
  );
}

function ToastProvider() {
  const { toasts, hideToast } = useUIStore();

  return <ToastContainer toasts={toasts} onClose={hideToast} />;
}

function AppContent() {
  return (
    <div className="layout">
      <Header />
      <main className="main-content">
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/lobby" element={<LobbyPage />} />
            <Route path="/game/:gameId" element={<GamePage />} />
            <Route path="/join/:shareCode" element={<JoinPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </main>
      <ToastProvider />
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </ErrorBoundary>
  );
}
