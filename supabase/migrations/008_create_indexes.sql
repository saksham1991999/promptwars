-- 008: Create indexes for performance

-- Games: player lookups, status filtering, join codes
CREATE INDEX IF NOT EXISTS idx_games_white_player ON games(white_player_id);
CREATE INDEX IF NOT EXISTS idx_games_black_player ON games(black_player_id);
CREATE INDEX IF NOT EXISTS idx_games_status ON games(status);
CREATE INDEX IF NOT EXISTS idx_games_share_code ON games(share_code);

-- Pieces: game lookup, active pieces
CREATE INDEX IF NOT EXISTS idx_pieces_game ON game_pieces(game_id);
CREATE INDEX IF NOT EXISTS idx_pieces_game_color ON game_pieces(game_id, color);

-- Moves: game history
CREATE INDEX IF NOT EXISTS idx_moves_game ON game_moves(game_id);
CREATE INDEX IF NOT EXISTS idx_moves_game_number ON game_moves(game_id, move_number);

-- Chat: message pagination
CREATE INDEX IF NOT EXISTS idx_chat_game_created ON chat_messages(game_id, created_at DESC);

-- Persuasion & Morale: game/piece lookups
CREATE INDEX IF NOT EXISTS idx_persuasion_game ON persuasion_attempts(game_id);
CREATE INDEX IF NOT EXISTS idx_morale_piece ON morale_events(piece_id);
