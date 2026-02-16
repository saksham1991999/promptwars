import { create } from 'zustand';
import type { ChatMessage } from '../types/game';
import { api } from '../lib/api';

interface ChatStore {
  // State
  messages: ChatMessage[];
  isLoading: boolean;
  hasMore: boolean;
  error: string | null;

  // Actions
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  addOptimisticMessage: (content: string, senderId: string) => string;
  confirmMessage: (tempId: string, message: ChatMessage) => void;
  removeMessage: (tempId: string) => void;
  loadMessages: (gameId: string) => Promise<void>;
  sendMessage: (gameId: string, content: string) => Promise<void>;
  reset: () => void;
}

const initialState = {
  messages: [],
  isLoading: false,
  hasMore: true,
  error: null,
};

export const useChatStore = create<ChatStore>((set, get) => ({
  ...initialState,

  setMessages: (messages) => set({ messages }),

  addMessage: (message) => {
    const { messages } = get();
    // Avoid duplicates
    if (messages.some((m) => m.id === message.id)) {
      return;
    }
    set({ messages: [...messages, message] });
  },

  addOptimisticMessage: (content, senderId) => {
    const tempId = `temp-${Date.now()}`;
    const optimisticMessage: ChatMessage = {
      id: tempId,
      sender_id: senderId,
      sender_name: 'You',
      message_type: 'player_message',
      content,
      created_at: new Date().toISOString(),
      metadata: { sending: true },
    };

    const { messages } = get();
    set({ messages: [...messages, optimisticMessage] });
    return tempId;
  },

  confirmMessage: (tempId, message) => {
    const { messages } = get();
    const updatedMessages = messages.map((m) =>
      m.id === tempId ? message : m
    );
    set({ messages: updatedMessages });
  },

  removeMessage: (tempId) => {
    const { messages } = get();
    const updatedMessages = messages.filter((m) => m.id !== tempId);
    set({ messages: updatedMessages });
  },

  loadMessages: async (gameId) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.getChatHistory(gameId);
      set({
        messages: response.data || [],
        isLoading: false,
        hasMore: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load messages',
        isLoading: false,
      });
    }
  },

  sendMessage: async (gameId, content) => {
    const tempId = get().addOptimisticMessage(content, 'user');

    try {
      const message = await api.sendChatMessage(gameId, content);
      get().confirmMessage(tempId, message);
    } catch (error) {
      get().removeMessage(tempId);
      set({
        error: error instanceof Error ? error.message : 'Failed to send message',
      });
    }
  },

  reset: () => set(initialState),
}));
