-- 004: Create game_moves table

CREATE TABLE IF NOT EXISTS public.game_moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES public.games(id) ON DELETE CASCADE,
    piece_id UUID REFERENCES public.game_pieces(id),
    player_id UUID REFERENCES public.profiles(id),
    move_number INT NOT NULL,
    from_square TEXT NOT NULL,
    to_square TEXT NOT NULL,
    san TEXT NOT NULL,
    fen_after TEXT NOT NULL,
    move_quality INT CHECK (move_quality >= 1 AND move_quality <= 10),
    evaluation FLOAT,
    analysis JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.game_moves ENABLE ROW LEVEL SECURITY;
