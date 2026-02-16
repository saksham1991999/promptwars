/** Chat Interface component — renders game chat with color-coded message types */
import { useState, useRef, useEffect, type ReactElement } from 'react';
import { MessageCircle, Send, Loader2, Swords, CheckCircle, XCircle, Bot, Lightbulb, Crown, Settings } from 'lucide-react';
import { useChatStore } from '../stores/chatStore';
import { Skeleton } from './ui';

interface ChatInterfaceProps {
    gameId: string;
    disabled?: boolean;
}

function formatTime(dateStr: string): string {
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getSenderIcon(type: string): ReactElement {
    switch (type) {
        case 'player_command': return <Swords size={14} />;
        case 'player_message': return <MessageCircle size={14} />;
        case 'piece_response': return <CheckCircle size={14} />;
        case 'piece_refusal': return <XCircle size={14} />;
        case 'ai_analysis': return <Bot size={14} />;
        case 'ai_suggestion': return <Lightbulb size={14} />;
        case 'king_taunt': return <Crown size={14} />;
        case 'king_reaction': return <Crown size={14} />;
        case 'system': return <Settings size={14} />;
        case 'persuasion_attempt': return <MessageCircle size={14} />;
        case 'persuasion_result': return <CheckCircle size={14} />;
        default: return <MessageCircle size={14} />;
    }
}

export default function ChatInterface({
    gameId,
    disabled = false,
}: ChatInterfaceProps) {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Get messages and loading state from store
    const messages = useChatStore((state) => state.messages);
    const isLoading = useChatStore((state) => state.isLoading);
    const sendMessage = useChatStore((state) => state.sendMessage);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        const trimmed = input.trim();
        if (!trimmed || disabled) return;

        setInput('');
        await sendMessage(gameId, trimmed);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const charCount = input.length;
    const maxChars = 500;
    const showWarning = charCount > maxChars * 0.8;

    return (
        <div className="chat-container">
            <div className="chat-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                    <MessageCircle size={20} />
                    <span className="chat-header-title">Battle Chat</span>
                </div>
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                    {messages.length} messages
                </span>
            </div>

            <div className="chat-messages">
                {isLoading && messages.length === 0 ? (
                    <div style={{ padding: 'var(--space-4)' }}>
                        <Skeleton variant="text" count={5} />
                    </div>
                ) : messages.length === 0 ? (
                    <div style={{ textAlign: 'center', color: 'var(--text-tertiary)', padding: 'var(--space-8)' }}>
                        <MessageCircle size={48} style={{ margin: '0 auto var(--space-4)', opacity: 0.5 }} />
                        <p style={{ fontSize: 'var(--text-base)', marginBottom: 'var(--space-2)' }}>Game chat will appear here</p>
                        <p style={{ fontSize: 'var(--text-xs)', marginTop: 'var(--space-2)' }}>
                            Command your pieces, watch them respond!
                        </p>
                    </div>
                ) : (
                    messages.map((msg) => (
                        <div key={msg.id} className={`chat-message chat-msg-${msg.message_type}`}>
                            <div className="chat-message-header">
                                <span className="chat-sender" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                                    {getSenderIcon(msg.message_type)}
                                    {msg.sender_name}
                                </span>
                                <span className="chat-timestamp">{formatTime(msg.created_at)}</span>
                            </div>
                            <div className="chat-bubble">
                                {msg.content}
                                {msg.metadata?.sending && (
                                    <Loader2 size={14} style={{ marginLeft: 'var(--space-2)', animation: 'spin 1s linear infinite' }} />
                                )}
                            </div>
                        </div>
                    ))
                )}

                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-container">
                <input
                    className="chat-input"
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value.slice(0, maxChars))}
                    onKeyDown={handleKeyDown}
                    placeholder={disabled ? 'Game is not active' : 'Type a message or command...'}
                    disabled={disabled}
                    aria-label="Chat message input"
                    maxLength={maxChars}
                />
                <button
                    className="chat-send-btn"
                    onClick={handleSend}
                    disabled={disabled || !input.trim()}
                    aria-label="Send message"
                    style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}
                >
                    <Send size={16} />
                    Send
                </button>
            </div>
            {input && (
                <div style={{
                    fontSize: 'var(--text-xs)',
                    color: showWarning ? 'var(--warning-500)' : 'var(--text-tertiary)',
                    padding: '0 var(--space-4) var(--space-2)',
                    textAlign: 'right',
                }}>
                    {charCount}/{maxChars}
                </div>
            )}
        </div>
    );
}
