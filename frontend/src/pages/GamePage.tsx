/** Game Page — main game screen with board, chat, and morale tracker */
import { useEffect, useCallback, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Chess, type Square } from 'chess.js';
import { Flag, Handshake, Loader2, Trophy, CheckCircle } from 'lucide-react';
import ChessBoard from '../components/ChessBoard';
import ChatInterface from '../components/ChatInterface';
import MoraleTracker from '../components/MoraleTracker';
import PersuasionModal from '../components/PersuasionModal';
import { api, getSessionId } from '../lib/api';
import { supabase } from '../lib/supabase';
import { useGameStore } from '../stores/gameStore';
import { useChatStore } from '../stores/chatStore';
import { useUIStore } from '../stores/uiStore';
import { Skeleton, Button, ErrorState } from '../components/ui';
import type {
    Game,
    PieceColor,
    CommandResponse,
    PersuasionResponse,
} from '../types/game';

export default function GamePage() {
    const { gameId } = useParams<{ gameId: string }>();
    const navigate = useNavigate();
    const sessionId = getSessionId();

    // Local state for non-global data
    const [game, setGame] = useState<Game | null>(null);
    const [persuasionResult, setPersuasionResult] = useState<PersuasionResponse | null>(null);
    const [persuasionLoading, setPersuasionLoading] = useState(false);
    const [commandLoading, setCommandLoading] = useState(false);
    const [isMoraleCollapsed, setIsMoraleCollapsed] = useState(true);

    // Global stores
    const {
        pieces,
        setPieces,
        selectedSquare,
        selectSquare,
        setLegalMoves,
        isLoading,
        setLoading,
        error,
        setError,
        chess,
        setChess,
    } = useGameStore();

    const {
        loadMessages,
        setMessages,
    } = useChatStore();

    const {
        persuasionModal,
        openPersuasion,
        showToast,
    } = useUIStore();

    // Determine player color from session
    const playerColor: PieceColor = game?.white_player?.id === sessionId ? 'white' : 'black';
    const isMyTurn = game?.turn === playerColor;

    // Load game data
    const loadGame = useCallback(async () => {
        if (!gameId) return;
        setLoading(true);
        try {
            const [gameData, chatData] = await Promise.all([
                api.getGame(gameId),
                api.getChatHistory(gameId),
            ]);
            setGame(gameData);
            setPieces(gameData.pieces);
            setMessages(chatData.data);
            setChess(new Chess(gameData.fen));
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load game');
        } finally {
            setLoading(false);
        }
    }, [gameId, setLoading, setPieces, setMessages, setChess, setError]);

    // Initial load
    useEffect(() => {
        loadGame();
    }, [loadGame]);

    // Load chat messages
    useEffect(() => {
        if (gameId) {
            loadMessages(gameId);
        }
    }, [gameId, loadMessages]);

    // Supabase Realtime subscriptions for live updates
    useEffect(() => {
        if (!gameId) return;

        const channel = supabase.channel(`game:${gameId}`);

        channel
            .on(
                'postgres_changes',
                {
                    event: '*',
                    schema: 'public',
                    table: 'games',
                    filter: `id=eq.${gameId}`,
                },
                () => {
                    loadGame();
                }
            )
            .on(
                'postgres_changes',
                {
                    event: '*',
                    schema: 'public',
                    table: 'game_pieces',
                    filter: `game_id=eq.${gameId}`,
                },
                () => {
                    loadGame();
                }
            )
            .on(
                'postgres_changes',
                {
                    event: 'INSERT',
                    schema: 'public',
                    table: 'chat_messages',
                    filter: `game_id=eq.${gameId}`,
                },
                () => {
                    loadMessages(gameId);
                }
            )
            .subscribe();

        return () => {
            supabase.removeChannel(channel);
        };
    }, [gameId, loadGame, loadMessages]);

    // Handle square click with optimistic UI
    const handleSquareClick = useCallback(
        async (square: string) => {
            if (!game || game.status !== 'active' || !isMyTurn || commandLoading) return;

            if (selectedSquare) {
                // Try to make a move
                const moves = chess.moves({ square: selectedSquare as Square, verbose: true });
                const isLegalMove = moves.some((m) => m.to === square);

                if (isLegalMove) {
                    const piece = pieces.find(
                        (p) => p.square === selectedSquare && p.color === playerColor && !p.is_captured
                    );

                    if (piece) {
                        setCommandLoading(true);

                        // Optimistic UI update
                        const chessCopy = new Chess(chess.fen());
                        try {
                            chessCopy.move({ from: selectedSquare as Square, to: square as Square });
                            setChess(chessCopy);
                            selectSquare(null);
                            setLegalMoves([]);
                        } catch {
                            // Move validation failed
                        }

                        try {
                            const response: CommandResponse = await api.issueCommand(game.id, {
                                piece_id: piece.id,
                                target_square: square,
                            });

                            // Update from server truth
                            if (response.board_state) {
                                setChess(new Chess(response.board_state.fen));
                                setGame((prev) =>
                                    prev ? { ...prev, fen: response.board_state.fen, turn: response.board_state.turn as PieceColor } : prev
                                );
                            }

                            // If piece refused, open persuasion modal
                            if (!response.move_executed && response.piece_response && !response.piece_response.will_move) {
                                openPersuasion(piece, square);
                                showToast(`${piece.piece_type} refused to move!`, 'warning');
                            } else if (response.move_executed) {
                                showToast('Move executed successfully', 'success');
                            }

                            // Refresh game state
                            await loadGame();
                        } catch (err) {
                            setError(err instanceof Error ? err.message : 'Failed to issue command');
                            showToast('Command failed', 'error');
                            // Rollback optimistic update
                            setChess(new Chess(game.fen));
                        } finally {
                            setCommandLoading(false);
                        }
                    }
                }

                selectSquare(null);
                setLegalMoves([]);
            } else {
                // Select a piece
                const piece = pieces.find(
                    (p) => p.square === square && p.color === playerColor && !p.is_captured
                );

                if (piece) {
                    selectSquare(square);
                }
            }
        },
        [game, selectedSquare, pieces, playerColor, isMyTurn, commandLoading, chess, selectSquare, setLegalMoves, setChess, setError, openPersuasion, showToast, loadGame]
    );

    // Handle persuasion
    const handlePersuade = async (argument: string) => {
        if (!game || !persuasionModal.piece) return;
        setPersuasionLoading(true);
        try {
            const result = await api.persuade(game.id, {
                piece_id: persuasionModal.piece.id,
                target_square: persuasionModal.target!,
                argument,
            });
            setPersuasionResult(result);

            if (result.move_executed && result.board_state) {
                setChess(new Chess(result.board_state.fen));
                setGame((prev) =>
                    prev ? { ...prev, fen: result.board_state!.fen, turn: result.board_state!.turn as PieceColor } : prev
                );
                showToast('Persuasion successful! Move executed.', 'success');
                await loadGame();
            } else {
                showToast('Persuasion failed', 'error');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Persuasion failed');
            showToast('Persuasion failed', 'error');
        } finally {
            setPersuasionLoading(false);
        }
    };

    // Handle resign
    const handleResign = async () => {
        if (!game || !confirm('Are you sure you want to resign?')) return;
        try {
            await api.resign(game.id);
            showToast('You resigned', 'info');
            await loadGame();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to resign');
            showToast('Failed to resign', 'error');
        }
    };

    // Handle offer draw
    const handleOfferDraw = async () => {
        if (!game) return;
        try {
            await api.offerDraw(game.id);
            showToast('Draw offer sent', 'info');
        } catch (err) {
            showToast('Failed to offer draw', 'error');
        }
    };

    // Get check square
    const checkSquare = chess.inCheck()
        ? pieces.find((p) => p.piece_type === 'king' && p.color === game?.turn && !p.is_captured)?.square || null
        : null;

    // Loading state
    if (isLoading && !game) {
        return (
            <div className="game-layout">
                <div className="game-left">
                    <Skeleton variant="rectangular" width="100%" height="600px" />
                </div>
                <div className="game-right" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                    <Skeleton variant="rectangular" height="200px" />
                    <Skeleton variant="rectangular" height="400px" />
                </div>
            </div>
        );
    }

    // Error state
    if (error && !game) {
        return (
            <ErrorState
                title="Failed to load game"
                message={error}
                retry={loadGame}
            />
        );
    }

    if (!game) {
        return (
            <ErrorState
                title="Game not found"
                message="The game you're looking for doesn't exist or has been deleted."
                retry={() => navigate('/')}
            />
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
                    marginBottom: 'var(--space-4)',
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                        {isMyTurn ? (
                            <>
                                <CheckCircle size={20} color="var(--success-500)" />
                                <span style={{
                                    fontSize: 'var(--text-sm)',
                                    fontWeight: 'var(--font-semibold)',
                                    color: 'var(--success-500)',
                                }}>
                                    Your Turn
                                </span>
                            </>
                        ) : (
                            <>
                                <Loader2 size={20} color="var(--text-tertiary)" style={{ animation: 'spin 2s linear infinite' }} />
                                <span style={{
                                    fontSize: 'var(--text-sm)',
                                    color: 'var(--text-tertiary)',
                                }}>
                                    Opponent's Turn
                                </span>
                            </>
                        )}
                        <span style={{ margin: '0 var(--space-2)', color: 'var(--text-tertiary)' }}>•</span>
                        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                            Playing as {playerColor}
                        </span>
                    </div>
                    <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleOfferDraw}
                            icon={<Handshake size={16} />}
                            disabled={game.status !== 'active'}
                        >
                            Draw
                        </Button>
                        <Button
                            variant="danger"
                            size="sm"
                            onClick={handleResign}
                            icon={<Flag size={16} />}
                            disabled={game.status !== 'active'}
                        >
                            Resign
                        </Button>
                    </div>
                </div>

                {/* Chess Board */}
                <ChessBoard
                    pieces={pieces}
                    playerColor={playerColor}
                    lastMove={null}
                    checkSquare={checkSquare}
                    onSquareClick={handleSquareClick}
                />

                {commandLoading && (
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'var(--space-2)',
                        color: 'var(--text-secondary)',
                        marginTop: 'var(--space-3)',
                    }}>
                        <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
                        Processing command...
                    </div>
                )}

                {/* Game result */}
                {game.status === 'completed' && (
                    <div className="card" style={{
                        textAlign: 'center',
                        background: 'rgba(99, 102, 241, 0.1)',
                        border: '1px solid var(--primary-500)',
                        marginTop: 'var(--space-4)',
                    }}>
                        <Trophy size={48} style={{ margin: '0 auto var(--space-3)', color: 'var(--primary-500)' }} />
                        <h2 style={{ marginBottom: 'var(--space-2)', fontSize: 'var(--text-2xl)' }}>
                            {game.result === 'white_wins' && playerColor === 'white' ? 'You Win!' :
                                game.result === 'black_wins' && playerColor === 'black' ? 'You Win!' :
                                    game.result === 'draw' ? 'Draw' :
                                        game.result === 'stalemate' ? 'Stalemate' :
                                            'You Lost'}
                        </h2>
                        <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)' }}>
                            {game.result?.replace('_', ' ')}
                        </p>
                        <Button
                            variant="primary"
                            onClick={() => navigate('/lobby')}
                            style={{ marginTop: 'var(--space-4)' }}
                        >
                            Play Again
                        </Button>
                    </div>
                )}
            </div>

            {/* Right: Chat + Morale */}
            <div className="game-right">
                <MoraleTracker
                    pieces={pieces}
                    playerColor={playerColor}
                    isCollapsed={isMoraleCollapsed}
                    onToggle={() => setIsMoraleCollapsed(!isMoraleCollapsed)}
                />

                <div style={{ flex: 1, minHeight: 0, marginTop: 'var(--space-4)' }}>
                    <ChatInterface
                        gameId={gameId!}
                        disabled={game.status !== 'active'}
                    />
                </div>
            </div>

            {/* Persuasion Modal */}
            <PersuasionModal
                onSubmit={handlePersuade}
                result={persuasionResult}
                isLoading={persuasionLoading}
            />
        </div>
    );
}
