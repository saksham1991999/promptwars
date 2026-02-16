/** Main App — routing, layout (no auth required) */
import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LobbyPage from './pages/LobbyPage';
import GamePage from './pages/GamePage';
import JoinPage from './pages/JoinPage';
import './App.css';

function Header() {
  return (
    <header className="header">
      <Link to="/" className="header-logo">
        <span className="gradient-text">♟ PromptWars</span>
      </Link>
      <nav className="header-nav">
        <Link to="/lobby" className="btn btn-primary btn-sm">⚔️ Play Now</Link>
      </nav>
    </header>
  );
}

function AppContent() {
  return (
    <div className="layout">
      <Header />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/lobby" element={<LobbyPage />} />
          <Route path="/game/:gameId" element={<GamePage />} />
          <Route path="/join/:shareCode" element={<JoinPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
