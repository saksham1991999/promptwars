-- 006: Create persuasion_attempts table

CREATE TABLE IF NOT EXISTS public.persuasion_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES public.games(id) ON DELETE CASCADE,
    piece_id UUID NOT NULL REFERENCES public.game_pieces(id),
    player_id UUID NOT NULL REFERENCES public.profiles(id),
    argument_text TEXT NOT NULL,
    is_voice BOOLEAN NOT NULL DEFAULT FALSE,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    success_probability FLOAT NOT NULL DEFAULT 0.0,
    piece_response TEXT,
    evaluation JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.persuasion_attempts ENABLE ROW LEVEL SECURITY;
