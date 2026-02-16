import { create } from 'zustand';
import type { GamePiece } from '../types/game';

interface PersuasionModal {
  isOpen: boolean;
  piece: GamePiece | null;
  target: string | null;
}

interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  visible: boolean;
}

interface UIStore {
  // State
  persuasionModal: PersuasionModal;
  toasts: Toast[];

  // Actions
  openPersuasion: (piece: GamePiece, target: string) => void;
  closePersuasion: () => void;
  showToast: (message: string, type: Toast['type'], duration?: number) => void;
  hideToast: (id: string) => void;
  clearToasts: () => void;
}

const initialState = {
  persuasionModal: {
    isOpen: false,
    piece: null,
    target: null,
  },
  toasts: [],
};

export const useUIStore = create<UIStore>((set, get) => ({
  ...initialState,

  openPersuasion: (piece, target) => {
    set({
      persuasionModal: {
        isOpen: true,
        piece,
        target,
      },
    });
  },

  closePersuasion: () => {
    set({
      persuasionModal: {
        isOpen: false,
        piece: null,
        target: null,
      },
    });
  },

  showToast: (message, type, duration = 5000) => {
    const id = `toast-${Date.now()}`;
    const toast: Toast = { id, message, type, visible: true };

    set((state) => ({
      toasts: [...state.toasts, toast],
    }));

    // Auto-hide after duration
    if (duration > 0) {
      setTimeout(() => {
        get().hideToast(id);
      }, duration);
    }
  },

  hideToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    }));
  },

  clearToasts: () => {
    set({ toasts: [] });
  },
}));
