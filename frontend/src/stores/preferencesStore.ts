import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface PreferencesStore {
  // State
  soundEnabled: boolean;
  reducedMotion: boolean;
  theme: 'dark' | 'light';

  // Actions
  toggleSound: () => void;
  toggleReducedMotion: () => void;
  setTheme: (theme: 'dark' | 'light') => void;
  reset: () => void;
}

const initialState = {
  soundEnabled: false,
  reducedMotion: false,
  theme: 'dark' as const,
};

export const usePreferencesStore = create<PreferencesStore>()(
  persist(
    (set) => ({
      ...initialState,

      toggleSound: () => set((state) => ({ soundEnabled: !state.soundEnabled })),

      toggleReducedMotion: () =>
        set((state) => {
          const newValue = !state.reducedMotion;
          // Apply to document for CSS media query override
          if (newValue) {
            document.documentElement.style.setProperty('--motion-duration', '0.01ms');
          } else {
            document.documentElement.style.removeProperty('--motion-duration');
          }
          return { reducedMotion: newValue };
        }),

      setTheme: (theme) => {
        set({ theme });
        document.documentElement.setAttribute('data-theme', theme);
      },

      reset: () => set(initialState),
    }),
    {
      name: 'chess-alive-preferences',
    }
  )
);
