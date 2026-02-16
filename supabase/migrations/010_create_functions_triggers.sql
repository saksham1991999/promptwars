-- 010: Functions and triggers

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_games_updated_at
    BEFORE UPDATE ON public.games
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER tr_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER tr_game_pieces_updated_at
    BEFORE UPDATE ON public.game_pieces
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- Update player stats when game completes
CREATE OR REPLACE FUNCTION public.update_player_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Only fire when status changes to 'completed'
    IF NEW.status = 'completed' AND (OLD.status IS NULL OR OLD.status != 'completed') THEN
        -- Update games_played for both players
        UPDATE public.profiles SET games_played = games_played + 1
        WHERE id IN (NEW.white_player_id, NEW.black_player_id);

        -- Update wins/losses/draws
        IF NEW.result = 'white_wins' THEN
            UPDATE public.profiles SET games_won = games_won + 1 WHERE id = NEW.white_player_id;
            UPDATE public.profiles SET games_lost = games_lost + 1 WHERE id = NEW.black_player_id;
        ELSIF NEW.result = 'black_wins' THEN
            UPDATE public.profiles SET games_won = games_won + 1 WHERE id = NEW.black_player_id;
            UPDATE public.profiles SET games_lost = games_lost + 1 WHERE id = NEW.white_player_id;
        ELSIF NEW.result IN ('draw', 'stalemate') THEN
            UPDATE public.profiles SET games_drawn = games_drawn + 1
            WHERE id IN (NEW.white_player_id, NEW.black_player_id);
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER tr_update_player_stats
    AFTER UPDATE ON public.games
    FOR EACH ROW EXECUTE FUNCTION public.update_player_stats();

-- Enable realtime for relevant tables
ALTER PUBLICATION supabase_realtime ADD TABLE public.chat_messages;
ALTER PUBLICATION supabase_realtime ADD TABLE public.game_pieces;
ALTER PUBLICATION supabase_realtime ADD TABLE public.games;
