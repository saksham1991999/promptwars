/** Auth context — provides authentication state across the app */
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { AuthState } from '../types/game';
import { supabase } from '../lib/supabase';
import { api } from '../lib/api';

interface AuthContextValue extends AuthState {
    login: (email: string, password: string) => Promise<void>;
    signup: (email: string, password: string, username?: string) => Promise<void>;
    logout: () => Promise<void>;
    refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [state, setState] = useState<AuthState>({
        user: null,
        accessToken: null,
        isAuthenticated: false,
        isLoading: true,
    });

    // Listen for Supabase auth state changes
    useEffect(() => {
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            async (_event, session) => {
                if (session?.user) {
                    try {
                        const profile = await api.getProfile();
                        setState({
                            user: profile,
                            accessToken: session.access_token,
                            isAuthenticated: true,
                            isLoading: false,
                        });
                    } catch {
                        setState({
                            user: {
                                id: session.user.id,
                                username: session.user.user_metadata?.username || `player_${session.user.id.slice(0, 8)}`,
                                email: session.user.email || '',
                                avatar_url: null,
                                games_played: 0, games_won: 0, games_lost: 0, games_drawn: 0,
                                settings: { theme: 'dark', sound: true, voice: true, contrast: false, motion: true },
                            },
                            accessToken: session.access_token,
                            isAuthenticated: true,
                            isLoading: false,
                        });
                    }
                } else {
                    setState({ user: null, accessToken: null, isAuthenticated: false, isLoading: false });
                }
            }
        );

        return () => subscription.unsubscribe();
    }, []);

    const login = useCallback(async (email: string, password: string) => {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
    }, []);

    const signup = useCallback(async (email: string, password: string, username?: string) => {
        const { error } = await supabase.auth.signUp({
            email,
            password,
            options: { data: username ? { username } : undefined },
        });
        if (error) throw error;
    }, []);

    const logout = useCallback(async () => {
        await supabase.auth.signOut();
    }, []);

    const refreshProfile = useCallback(async () => {
        try {
            const profile = await api.getProfile();
            setState((prev) => ({ ...prev, user: profile }));
        } catch { /* ignore */ }
    }, []);

    return (
        <AuthContext.Provider value={{ ...state, login, signup, logout, refreshProfile }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
}
