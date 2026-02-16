-- 003: Create game_pieces table

CREATE TABLE IF NOT EXISTS public.game_pieces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES public.games(id) ON DELETE CASCADE,
    color TEXT NOT NULL CHECK (color IN ('white', 'black')),
    piece_type TEXT NOT NULL CHECK (piece_type IN (
        'pawn', 'knight', 'bishop', 'rook', 'queen', 'king',
        'chancellor', 'archbishop', 'amazon', 'camel', 'nightrider',
        'grasshopper', 'cannon', 'berolina_pawn'
    )),
    square TEXT,
    morale INT NOT NULL DEFAULT 70 CHECK (morale >= 0 AND morale <= 100),
    personality JSONB NOT NULL DEFAULT '{
        "archetype": "default",
        "traits": [],
        "dialogue_style": "neutral"
    }'::jsonb,
    custom_config JSONB,
    is_captured BOOLEAN NOT NULL DEFAULT FALSE,
    is_promoted BOOLEAN NOT NULL DEFAULT FALSE,
    promoted_to TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.game_pieces ENABLE ROW LEVEL SECURITY;
