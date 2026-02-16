import type { ChatMessage, MessageType } from '../../types/game'

interface ChatMessageOverrides {
  id?: string
  message_type?: MessageType
  sender_id?: string
  sender_name?: string
  content?: string
  metadata?: Record<string, unknown>
  created_at?: string
}

export const createChatMessage = (overrides: ChatMessageOverrides = {}): ChatMessage => ({
  id: overrides.id ?? `msg-${Math.random().toString(36).substr(2, 9)}`,
  message_type: overrides.message_type ?? 'player_message',
  sender_id: overrides.sender_id,
  sender_name: overrides.sender_name ?? 'Test Player',
  content: overrides.content ?? 'Test message content',
  metadata: overrides.metadata ?? {},
  created_at: overrides.created_at ?? new Date().toISOString(),
})

export const createPlayerMessage = (content: string, overrides: Partial<ChatMessageOverrides> = {}): ChatMessage =>
  createChatMessage({
    message_type: 'player_message',
    sender_name: 'Player',
    content,
    ...overrides,
  })

export const createPieceResponse = (content: string, overrides: Partial<ChatMessageOverrides> = {}): ChatMessage =>
  createChatMessage({
    message_type: 'piece_response',
    sender_name: 'White Knight',
    content,
    ...overrides,
  })

export const createPieceRefusal = (content: string, overrides: Partial<ChatMessageOverrides> = {}): ChatMessage =>
  createChatMessage({
    message_type: 'piece_refusal',
    sender_name: 'White Knight',
    content,
    ...overrides,
  })

export const createAiAnalysis = (content: string, overrides: Partial<ChatMessageOverrides> = {}): ChatMessage =>
  createChatMessage({
    message_type: 'ai_analysis',
    sender_name: 'AI Analyst',
    content,
    ...overrides,
  })

export const createKingTaunt = (content: string, overrides: Partial<ChatMessageOverrides> = {}): ChatMessage =>
  createChatMessage({
    message_type: 'king_taunt',
    sender_name: 'Black King',
    content,
    ...overrides,
  })

export const createSystemMessage = (content: string, overrides: Partial<ChatMessageOverrides> = {}): ChatMessage =>
  createChatMessage({
    message_type: 'system',
    sender_name: 'System',
    content,
    ...overrides,
  })
