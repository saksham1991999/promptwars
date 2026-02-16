-- 011: Alter black_player_id to allow 'ai' text value for AI games

-- Drop policies that depend on black_player_id
DROP POLICY IF EXISTS "Anyone can view waiting games or own games" ON public.games;
DROP POLICY IF EXISTS "Participants can update games" ON public.games;
DROP POLICY IF EXISTS "Game participants can view pieces" ON public.game_pieces;
DROP POLICY IF EXISTS "Game participants can view moves" ON public.game_moves;
DROP POLICY IF EXISTS "Game participants can view chat" ON public.chat_messages;
DROP POLICY IF EXISTS "Game participants can send messages" ON public.chat_messages;
DROP POLICY IF EXISTS "Game participants can view persuasion" ON public.persuasion_attempts;
DROP POLICY IF EXISTS "Game participants can view morale events" ON public.morale_events;

-- Drop the foreign key constraint
ALTER TABLE public.games DROP CONSTRAINT IF EXISTS games_black_player_id_fkey;

-- Alter the column type to TEXT to allow 'ai' string
ALTER TABLE public.games ALTER COLUMN black_player_id TYPE TEXT;

-- Recreate policies with text comparison
CREATE POLICY "Anyone can view waiting games or own games"
    ON public.games FOR SELECT
    USING (
        status = 'waiting'
        OR white_player_id::text = auth.uid()::text
        OR black_player_id = auth.uid()::text
    );

CREATE POLICY "Participants can update games"
    ON public.games FOR UPDATE
    USING (
        white_player_id::text = auth.uid()::text
        OR black_player_id = auth.uid()::text
    );

CREATE POLICY "Game participants can view pieces"
    ON public.game_pieces FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = game_pieces.game_id
            AND (games.white_player_id::text = auth.uid()::text OR games.black_player_id = auth.uid()::text)
        )
    );

CREATE POLICY "Game participants can view moves"
    ON public.game_moves FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = game_moves.game_id
            AND (games.white_player_id::text = auth.uid()::text OR games.black_player_id = auth.uid()::text)
        )
    );

CREATE POLICY "Game participants can view chat"
    ON public.chat_messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = chat_messages.game_id
            AND (games.white_player_id::text = auth.uid()::text OR games.black_player_id = auth.uid()::text)
        )
    );

CREATE POLICY "Game participants can send messages"
    ON public.chat_messages FOR INSERT
    WITH CHECK (
        auth.uid() = sender_id
        AND EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = chat_messages.game_id
            AND (games.white_player_id::text = auth.uid()::text OR games.black_player_id = auth.uid()::text)
        )
    );

CREATE POLICY "Game participants can view persuasion"
    ON public.persuasion_attempts FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = persuasion_attempts.game_id
            AND (games.white_player_id::text = auth.uid()::text OR games.black_player_id = auth.uid()::text)
        )
    );

CREATE POLICY "Game participants can view morale events"
    ON public.morale_events FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = morale_events.game_id
            AND (games.white_player_id::text = auth.uid()::text OR games.black_player_id = auth.uid()::text)
        )
    );
