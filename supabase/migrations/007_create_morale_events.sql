-- 007: Create morale_events table

CREATE TABLE IF NOT EXISTS public.morale_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES public.games(id) ON DELETE CASCADE,
    piece_id UUID NOT NULL REFERENCES public.game_pieces(id),
    event_type TEXT NOT NULL CHECK (event_type IN (
        'capture_enemy', 'friendly_captured', 'endangered', 'protected',
        'blunder', 'idle', 'compliment', 'promotion', 'good_position',
        'clever_tactic', 'game_start', 'persuasion_success', 'persuasion_fail',
        'player_lied'
    )),
    morale_change INT NOT NULL,
    morale_after INT NOT NULL CHECK (morale_after >= 0 AND morale_after <= 100),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.morale_events ENABLE ROW LEVEL SECURITY;
