-- 009: Row Level Security policies

-- PROFILES
CREATE POLICY "Anyone can view profiles"
    ON public.profiles FOR SELECT
    USING (true);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- GAMES
CREATE POLICY "Anyone can view waiting games or own games"
    ON public.games FOR SELECT
    USING (
        status = 'waiting'
        OR white_player_id = auth.uid()
        OR black_player_id = auth.uid()
    );

CREATE POLICY "Authenticated users can create games"
    ON public.games FOR INSERT
    WITH CHECK (auth.uid() = white_player_id);

CREATE POLICY "Participants can update games"
    ON public.games FOR UPDATE
    USING (
        white_player_id = auth.uid()
        OR black_player_id = auth.uid()
    );

-- GAME_PIECES (managed by backend service role, read by participants)
CREATE POLICY "Game participants can view pieces"
    ON public.game_pieces FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = game_pieces.game_id
            AND (games.white_player_id = auth.uid() OR games.black_player_id = auth.uid())
        )
    );

CREATE POLICY "Service role manages pieces"
    ON public.game_pieces FOR ALL
    USING (auth.role() = 'service_role');

-- GAME_MOVES
CREATE POLICY "Game participants can view moves"
    ON public.game_moves FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = game_moves.game_id
            AND (games.white_player_id = auth.uid() OR games.black_player_id = auth.uid())
        )
    );

CREATE POLICY "Service role manages moves"
    ON public.game_moves FOR ALL
    USING (auth.role() = 'service_role');

-- CHAT_MESSAGES
CREATE POLICY "Game participants can view chat"
    ON public.chat_messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = chat_messages.game_id
            AND (games.white_player_id = auth.uid() OR games.black_player_id = auth.uid())
        )
    );

CREATE POLICY "Game participants can send messages"
    ON public.chat_messages FOR INSERT
    WITH CHECK (
        auth.uid() = sender_id
        AND EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = chat_messages.game_id
            AND (games.white_player_id = auth.uid() OR games.black_player_id = auth.uid())
        )
    );

-- PERSUASION_ATTEMPTS
CREATE POLICY "Game participants can view persuasion"
    ON public.persuasion_attempts FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = persuasion_attempts.game_id
            AND (games.white_player_id = auth.uid() OR games.black_player_id = auth.uid())
        )
    );

CREATE POLICY "Service role manages persuasion"
    ON public.persuasion_attempts FOR ALL
    USING (auth.role() = 'service_role');

-- MORALE_EVENTS
CREATE POLICY "Game participants can view morale events"
    ON public.morale_events FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.games
            WHERE games.id = morale_events.game_id
            AND (games.white_player_id = auth.uid() OR games.black_player_id = auth.uid())
        )
    );

CREATE POLICY "Service role manages morale events"
    ON public.morale_events FOR ALL
    USING (auth.role() = 'service_role');
