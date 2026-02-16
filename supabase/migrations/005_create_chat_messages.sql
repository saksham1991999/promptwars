-- 005: Create chat_messages table

CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES public.games(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES public.profiles(id),
    message_type TEXT NOT NULL CHECK (message_type IN (
        'player_command', 'player_message', 'piece_response', 'piece_refusal',
        'ai_analysis', 'ai_suggestion', 'king_taunt', 'king_reaction',
        'system', 'persuasion_attempt', 'persuasion_result'
    )),
    sender_name TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
