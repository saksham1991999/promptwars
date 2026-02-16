/** Chat Interface component — renders game chat with color-coded message types */
import { useState, useRef, useEffect } from 'react';
import type { ChatMessage as ChatMessageType } from '../types/game';

interface ChatInterfaceProps {
    messages: ChatMessageType[];
    onSendMessage: (content: string) => void;
    isLoading?: boolean;
    disabled?: boolean;
}

function formatTime(dateStr: string): string {
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getSenderEmoji(type: string): string {
    switch (type) {
        case 'player_command': return '🎯';
        case 'player_message': return '💬';
        case 'piece_response': return '✅';
        case 'piece_refusal': return '❌';
        case 'ai_analysis': return '🤖';
        case 'ai_suggestion': return '💡';
        case 'king_taunt': return '👑';
        case 'king_reaction': return '😤';
        case 'system': return '⚙️';
        case 'persuasion_attempt': return '🗣️';
        case 'persuasion_result': return '🎲';
        default: return '💬';
    }
}

export default function ChatInterface({
    messages,
    onSendMessage,
    isLoading = false,
    disabled = false,
}: ChatInterfaceProps) {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = () => {
        const trimmed = input.trim();
        if (!trimmed) return;
        onSendMessage(trimmed);
        setInput('');
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <span className="chat-header-title">💬 Battle Chat</span>
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                    {messages.length} messages
                </span>
            </div>

            <div className="chat-messages">
                {messages.length === 0 && (
                    <div style={{ textAlign: 'center', color: 'var(--text-tertiary)', padding: 'var(--space-8)' }}>
                        <p style={{ fontSize: 'var(--text-2xl)', marginBottom: 'var(--space-2)' }}>♟️</p>
                        <p>Game chat will appear here...</p>
                        <p style={{ fontSize: 'var(--text-xs)', marginTop: 'var(--space-2)' }}>
                            Command your pieces, watch them respond!
                        </p>
                    </div>
                )}

                {messages.map((msg) => (
                    <div key={msg.id} className={`chat-message chat-msg-${msg.message_type}`}>
                        <div className="chat-message-header">
                            <span className="chat-sender">
                                {getSenderEmoji(msg.message_type)} {msg.sender_name}
                            </span>
                            <span className="chat-timestamp">{formatTime(msg.created_at)}</span>
                        </div>
                        <div className="chat-bubble">{msg.content}</div>
                    </div>
                ))}

                {isLoading && (
                    <div className="chat-message chat-msg-system">
                        <div className="chat-bubble" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                            <div className="spinner spinner-sm" />
                            Thinking...
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-container">
                <input
                    className="chat-input"
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={disabled ? 'Game is not active' : 'Type a message or command...'}
                    disabled={disabled}
                    aria-label="Chat message input"
                />
                <button
                    className="chat-send-btn"
                    onClick={handleSend}
                    disabled={disabled || !input.trim()}
                    aria-label="Send message"
                >
                    Send
                </button>
            </div>
        </div>
    );
}
