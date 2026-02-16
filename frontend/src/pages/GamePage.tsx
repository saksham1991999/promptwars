/** Game Page — main game screen with board, chat, and morale tracker (session-based) */
import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Chess, type Square } from 'chess.js';
import ChessBoard from '../components/ChessBoard';
import ChatInterface from '../components/ChatInterface';
import MoraleTracker from '../components/MoraleTracker';
import PersuasionModal from '../components/PersuasionModal';
import { api, getSessionId } from '../lib/api';
import type {
    Game,
    GamePiece,
    ChatMessage,
    PieceColor,
    CommandResponse,
    PersuasionResponse,
} from '../types/game';

export default function GamePage() {
    const { gameId } = useParams<{ gameId: string }>();
    const sessionId = getSessionId();

    const [game, setGame] = useState<Game | null>(null);
    const [pieces, setPieces] = useState<GamePiece[]>([]);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
    const [legalMoves, setLegalMoves] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [commandLoading, setCommandLoading] = useState(false);
    const [error, setError] = useState('');

    // Persuasion
    const [persuasionPiece, setPersuasionPiece] = useState<GamePiece | null>(null);
    const [persuasionTarget, setPersuasionTarget] = useState<string>('');
    const [persuasionResult, setPersuasionResult] = useState<PersuasionResponse | null>(null);
    const [persuasionLoading, setPersuasionLoading] = useState(false);

    // Chess.js instance
    const [chess, setChess] = useState<Chess>(new Chess());

    // Polling ref
    const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

    // Determine player color from session
    const playerColor: PieceColor = game?.white_player?.id === sessionId ? 'white' : 'black';
    const isMyTurn = game?.turn === playerColor;

    // Load game data
    const loadGame = useCallback(async () => {
        if (!gameId) return;
        try {
            const [gameData, chatData] = await Promise.all([
                api.getGame(gameId),
                api.getChatHistory(gameId),
            ]);
            setGame(gameData);
            setPieces(gameData.pieces);
            setMessages(chatData.data as ChatMessage[]);
            setChess(new Chess(gameData.fen));
            setError('');
        } catch {
            setError('Failed to load game');
        } finally {
            setLoading(false);
        }
    }, [gameId]);

    // Initial load
    useEffect(() => {
        loadGame();
    }, [loadGame]);

    // Poll for updates every 3 seconds (replaces Supabase realtime)
    useEffect(() => {
        if (!gameId) return;

        pollRef.current = setInterval(() => {
            loadGame();
        }, 3000);

        return () => {
            if (pollRef.current) clearInterval(pollRef.current);
        };
    }, [gameId, loadGame]);

    // Handle square click
    const handleSquareClick = useCallback(
        async (square: string) => {
            if (!game || game.status !== 'active' || !isMyTurn || commandLoading) return;

            if (selectedSquare) {
                // Try to make a move
                if (legalMoves.includes(square)) {
                    const piece = pieces.find(
                        (p) => p.square === selectedSquare && p.color === playerColor && !p.is_captured
                    );

                    if (piece) {
                        setCommandLoading(true);
                        try {
                            const response: CommandResponse = await api.issueCommand(game.id, {
                                piece_id: piece.id,
                                target_square: square,
                            });

                            // Update game state from response
                            if (response.board_state) {
                                setChess(new Chess(response.board_state.fen));
                                setGame((prev) =>
                                    prev ? { ...prev, fen: response.board_state.fen, turn: response.board_state.turn as PieceColor } : prev
                                );
                            }

                            // If piece refused, open persuasion modal
                            if (!response.move_executed && response.piece_response && !response.piece_response.will_move) {
                                setPersuasionPiece(piece);
                                setPersuasionTarget(square);
                                setPersuasionResult(null);
                            }

                            // Refresh pieces and chat
                            const updatedGame = await api.getGame(game.id);
                            setPieces(updatedGame.pieces);

                            const chatData = await api.getChatHistory(game.id);
                            setMessages(chatData.data as ChatMessage[]);
                        } catch {
                            setError('Failed to issue command');
                        } finally {
                            setCommandLoading(false);
                        }
                    }
                }

                setSelectedSquare(null);
                setLegalMoves([]);
            } else {
                // Select a piece
                const piece = pieces.find(
                    (p) => p.square === square && p.color === playerColor && !p.is_captured
                );

                if (piece) {
                    setSelectedSquare(square);
                    try {
                        const moves = chess.moves({ square: square as Square, verbose: true });
                        setLegalMoves(moves.map((m) => m.to));
                    } catch {
                        setLegalMoves([]);
                    }
                }
            }
        },
        [game, selectedSquare, legalMoves, pieces, playerColor, isMyTurn, commandLoading, chess]
    );

    // Handle persuasion
    const handlePersuade = async (argument: string) => {
        if (!game || !persuasionPiece) return;
        setPersuasionLoading(true);
        try {
            const result = await api.persuade(game.id, {
                piece_id: persuasionPiece.id,
                target_square: persuasionTarget,
                argument,
            });
            setPersuasionResult(result);

            if (result.move_executed && result.board_state) {
                setChess(new Chess(result.board_state.fen));
                setGame((prev) =>
                    prev ? { ...prev, fen: result.board_state!.fen, turn: result.board_state!.turn as PieceColor } : prev
                );
                const updatedGame = await api.getGame(game.id);
                setPieces(updatedGame.pieces);
            }

            // Refresh chat
            const chatData = await api.getChatHistory(game.id);
            setMessages(chatData.data as ChatMessage[]);
        } catch {
            setError('Persuasion failed');
        } finally {
            setPersuasionLoading(false);
        }
    };

    // Handle chat
    const handleSendMessage = async (content: string) => {
        if (!gameId) return;
        try {
            await api.sendChatMessage(gameId, content);
            // Immediately refresh chat
            const chatData = await api.getChatHistory(gameId);
            setMessages(chatData.data as ChatMessage[]);
        } catch {
            /* ignore */
        }
    };

    // Handle resign
    const handleResign = async () => {
        if (!game || !confirm('Are you sure you want to resign?')) return;
        try {
            await api.resign(game.id);
            await loadGame();
        } catch {
            setError('Failed to resign');
        }
    };

    // Get check square
    const checkSquare = chess.inCheck()
        ? pieces.find((p) => p.piece_type === 'king' && p.color === game?.turn && !p.is_captured)?.square || null
        : null;

    if (loading) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
                <div style={{ textAlign: 'center' }}>
                    <div className="spinner spinner-lg" style={{ margin: '0 auto var(--space-4)' }} />
                    <p style={{ color: 'var(--text-secondary)' }}>Loading game...</p>
                </div>
            </div>
        );
    }

    if (!game) {
        return (
            <div style={{ textAlign: 'center', padding: 'var(--space-16)', color: 'var(--text-error)' }}>
                {error || 'Game not found'}
            </div>
        );
    }

    return (
        <div className="game-layout">
            {/* Left: Board */}
            <div className="game-left">
                {/* Status bar */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    width: '100%',
                    maxWidth: 'var(--board-size)',
                    alignItems: 'center',
                }}>
                    <div>
                        <span style={{
                            fontSize: 'var(--text-sm)',
                            fontWeight: 'var(--font-bold)',
                            color: isMyTurn ? 'var(--morale-high)' : 'var(--text-secondary)',
                        }}>
                            {isMyTurn ? '🟢 Your Turn' : '⏳ Opponent\'s Turn'}
                        </span>
                        <span style={{ margin: '0 var(--space-2)', color: 'var(--text-tertiary)' }}>•</span>
                        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                            Playing as {playerColor}
                        </span>
                    </div>
                    <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                        <button className="btn btn-ghost btn-sm" onClick={() => api.offerDraw(game.id)}>
                            🤝 Draw
                        </button>
                        <button className="btn btn-ghost btn-sm" onClick={handleResign} style={{ color: 'var(--text-error)' }}>
                            🏳️ Resign
                        </button>
                    </div>
                </div>

                {/* Chess Board */}
                <ChessBoard
                    pieces={pieces}
                    playerColor={playerColor}
                    lastMove={null}
                    checkSquare={checkSquare}
                    legalMoves={legalMoves}
                    selectedSquare={selectedSquare}
                    onSquareClick={handleSquareClick}
                />

                {commandLoading && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--text-secondary)' }}>
                        <div className="spinner spinner-sm" />
                        Processing command...
                    </div>
                )}

                {/* Game result */}
                {game.status === 'completed' && (
                    <div className="card" style={{
                        textAlign: 'center',
                        background: 'rgba(108, 99, 255, 0.1)',
                        border: '1px solid var(--accent-primary)',
                    }}>
                        <h2 style={{ marginBottom: 'var(--space-2)' }}>
                            {game.result === 'white_wins' && playerColor === 'white' ? '🎉 You Win!' :
                                game.result === 'black_wins' && playerColor === 'black' ? '🎉 You Win!' :
                                    game.result === 'draw' ? '🤝 Draw' :
                                        game.result === 'stalemate' ? '♟️ Stalemate' :
                                            '😔 You Lost'}
                        </h2>
                        <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)' }}>
                            {game.result?.replace('_', ' ')}
                        </p>
                    </div>
                )}
            </div>

            {/* Right: Chat + Morale */}
            <div className="game-right">
                <MoraleTracker pieces={pieces} playerColor={playerColor} />

                <div style={{ flex: 1, minHeight: 0 }}>
                    <ChatInterface
                        messages={messages}
                        onSendMessage={handleSendMessage}
                        isLoading={commandLoading}
                        disabled={game.status !== 'active'}
                    />
                </div>
            </div>

            {/* Persuasion Modal */}
            {persuasionPiece && (
                <PersuasionModal
                    piece={persuasionPiece}
                    targetSquare={persuasionTarget}
                    onSubmit={handlePersuade}
                    onClose={() => {
                        setPersuasionPiece(null);
                        setPersuasionResult(null);
                    }}
                    result={persuasionResult}
                    isLoading={persuasionLoading}
                />
            )}
        </div>
    );
}
