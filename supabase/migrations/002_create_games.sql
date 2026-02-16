-- 002: Create games table

CREATE TABLE IF NOT EXISTS public.games (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    white_player_id UUID REFERENCES public.profiles(id),
    black_player_id UUID REFERENCES public.profiles(id),
    status TEXT NOT NULL DEFAULT 'waiting'
        CHECK (status IN ('waiting', 'setup', 'active', 'completed', 'abandoned')),
    game_mode TEXT NOT NULL DEFAULT 'pvp'
        CHECK (game_mode IN ('pvp', 'pvai')),
    template TEXT NOT NULL DEFAULT 'classic'
        CHECK (template IN ('classic', 'power_chess', 'leaper_madness', 'hopper_havoc', 'pawn_revolution')),
    fen TEXT NOT NULL DEFAULT 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    pgn TEXT NOT NULL DEFAULT '',
    turn TEXT NOT NULL DEFAULT 'white'
        CHECK (turn IN ('white', 'black')),
    result TEXT DEFAULT NULL
        CHECK (result IS NULL OR result IN ('white_wins', 'black_wins', 'draw', 'stalemate', 'abandoned')),
    settings JSONB NOT NULL DEFAULT '{"surprise_mode": false, "turn_timer": null, "ai_difficulty": "medium"}'::jsonb,
    share_code TEXT UNIQUE NOT NULL DEFAULT encode(gen_random_bytes(6), 'hex'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);

ALTER TABLE public.games ENABLE ROW LEVEL SECURITY;
